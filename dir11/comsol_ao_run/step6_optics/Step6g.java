import com.comsol.model.*;
import com.comsol.model.util.*;
import java.util.*;
import java.util.Locale;

/** Step 6g: mode characterisation (u/v/w, strain-energy distribution) of the main and low peaks. Built on Step 6f: on the 6e model (6d-2 V2 geometry): low-band drive sweep + admittance, eigenmodes on the 6e mesh, power normalisation, sensitivity (eta, ridge offset). */
public class Step6g {
  static final String PZ="D:\\COMSOL63\\Multiphysics\\data\\comsol_piezo_lib.mph";
  static final String BASIC="D:\\COMSOL63\\Multiphysics\\data\\comsol_basic_material_lib.mph";
  static final double P_UM=2.71043685;
  static final int NP=15, ID=7, NH=7;
  static final int[] DEF={6,7,8};
  static final double WR=1.0e-6, HLN=400e-9, HAL=100e-9, HAIR=2e-6;
  static final double NO=2.211, NEX=2.138, N_AL=1.44, K_AL=16.0, LAM=1.55e-6;
  static final double K0=2*Math.PI/LAM;
  static final double P=P_UM*1e-6, LS=NP*P, XC0=(ID+0.5)*P;
  static final double FA_T_UNIT=0.0608, FA_P_UNIT=0.0896;
  static double XC=XC0;

  public static void main(String[] args){
    try{
      ModelUtil.initStandalone(true);
      System.out.println("STEP6G_START");
      System.out.println(String.format(Locale.US,"CFG p_um=%.8f NP=%d ID=%d def=%s hLn_nm=400 ridge=1.0um x 100nm air=2um mesh LN30/Al10/air150 nm, eta_s=5e-4 (base)",P_UM,NP,ID,Arrays.toString(DEF)));

      Model m=ModelUtil.create("M6g");
      int[][] G=build(m,100e-9,true);
      Set<String> sb=new HashSet<>(Arrays.asList(m.sol().tags()));
      m.study().create("stdD"); m.study("stdD").create("freq","Frequency");
      m.study("stdD").feature("freq").set("plist","3.3187[GHz], 3.33855[GHz]");
      try{ m.study("stdD").feature("freq").setEntry("activate","ewfd",false); }catch(Throwable t){ System.out.println("WARN deactivate ewfd: "+t.getMessage()); }
      m.study("stdD").createAutoSequences("all");
      String sd=null; for(String t:m.sol().tags()) if(!sb.contains(t)){ sd=t; break; }
      m.study("stdD").run();
      m.result().dataset().create("ds_stdD","Solution"); m.result().dataset("ds_stdD").set("solution",sd);
      characterise(m,"ds_stdD","DRV",0,99);

      m.component("comp1").physics("es").feature("term1").active(false);
      m.component("comp1").physics("es").create("gndT","Ground",1); m.component("comp1").physics("es").feature("gndT").selection().set(G[0]);
      sb=new HashSet<>(Arrays.asList(m.sol().tags()));
      m.study().create("stdE"); m.study("stdE").create("eig","Eigenfrequency");
      m.study("stdE").feature("eig").set("neigs","12");
      m.study("stdE").feature("eig").set("shift","3.33[GHz]");
      m.study("stdE").feature("eig").set("shiftactive","on");
      try{ m.study("stdE").feature("eig").setEntry("activate","ewfd",false); }catch(Throwable t){ System.out.println("WARN deactivate ewfd eig: "+t.getMessage()); }
      m.study("stdE").createAutoSequences("all");
      String se=null; for(String t:m.sol().tags()) if(!sb.contains(t)){ se=t; break; }
      m.study("stdE").run();
      m.result().dataset().create("ds_stdE","Solution"); m.result().dataset("ds_stdE").set("solution",se);
      characterise(m,"ds_stdE","EIG",3.29,3.36);
      System.out.println("STEP6G_DONE");
    }catch(Throwable t){ System.out.println("STEP6G_ABORT"); t.printStackTrace(System.out); }
  }

  static final String DEFR="((x>=6*p)*(x<9*p))", RIDGE="(y>"+String.format(Locale.US,"%.6e",HLN)+"[m])";

  static String wAvg(String S,String[] c){
    String[] e={"solid.eXX","solid.eYY","solid.eZZ","solid.eXY","solid.eXZ","solid.eYZ"};
    StringBuilder b=new StringBuilder("0.25*real(");
    for(int i=0;i<6;i++){ if(i>0) b.append("+"); b.append(i<3?"":"2*").append(S).append(c[i]).append("*conj(").append(e[i]).append(")"); }
    return b.append(")").toString();
  }

  /** prints u/v/w fractions and time-averaged strain-energy split (defect / finger cells / ridge / Al, per cell) for every solution in [fmin,fmax] GHz */
  static void characterise(Model m,String ds,String lab,double fmin,double fmax){
    String W=null;
    String[][] cand={{"solid.S","XX","YY","ZZ","XY","XZ","YZ"},{"solid.s","xx","yy","zz","xy","xz","yz"}};
    for(String[] cd:cand){
      String t=wAvg(cd[0],Arrays.copyOfRange(cd,1,7));
      try{ evalGC(m,ds,new String[]{"intLN("+t+")"}); W=t; System.out.println("WEXPR6G "+lab+" stress="+cd[0]+cd[1]+"... ok"); break; }
      catch(Throwable e){ System.out.println("WEXPR6G "+lab+" stress="+cd[0]+cd[1]+"... failed: "+e.getMessage()); }
    }
    if(W==null){ W="solid.Ws"; System.out.println("WEXPR6G "+lab+" fallback solid.Ws (instantaneous)"); }
    List<String> ex=new ArrayList<>();
    ex.add("freq");
    ex.add("intLN(abs(u)^2)"); ex.add("intLN(abs(v)^2)"); ex.add("intLN(abs(w)^2)");
    ex.add("intLN(abs(u)^2*"+DEFR+")"); ex.add("intLN(abs(v)^2*"+DEFR+")"); ex.add("intLN(abs(w)^2*"+DEFR+")");
    ex.add("intLN("+W+")"); ex.add("intLN("+W+"*"+DEFR+")"); ex.add("intLN("+W+"*"+RIDGE+")"); ex.add("intAl("+W+")");
    for(int c=0;c<NP;c++) ex.add("intLN("+W+"*(x>="+c+"*p)*(x<"+(c+1)+"*p))");
    double[][][] r=evalGC(m,ds,ex.toArray(new String[0]));
    double[][] re=r[0], im=r[1];
    for(int k=0;k<re[0].length;k++){
      double f=re[0][k]/1e9;
      if(f<fmin||f>fmax) continue;
      double q=im[0][k]!=0?re[0][k]/(2*Math.abs(im[0][k])):Double.NaN;
      double U=re[1][k],V=re[2][k],Wd=re[3][k],T=U+V+Wd, Td=re[4][k]+re[5][k]+re[6][k];
      double eLN=re[7][k], eDef=re[8][k], eRg=re[9][k], eAl=re[10][k], eTot=eLN+eAl;
      System.out.println(String.format(Locale.US,"CHAR6G set=%s k=%d f_GHz=%.6f Q=%.1f u_frac=%.4f v_frac=%.4f w_frac=%.4f disp_defect_frac=%.4f defect_uvw=(%.4f,%.4f,%.4f) E_defect/E_LN=%.4f E_fingercells/E_LN=%.4f E_ridge/E_LN=%.4f E_Al/(E_LN+E_Al)=%.4f",
        lab,k,f,q,U/T,V/T,Wd/T,Td/T,re[4][k]/Td,re[5][k]/Td,re[6][k]/Td,eDef/eLN,(eLN-eDef)/eLN,eRg/eLN,eAl/eTot));
      StringBuilder sc=new StringBuilder(String.format(Locale.US,"CELL6G set=%s k=%d f_GHz=%.6f E_cell/E_LN=",lab,k,f));
      for(int c=0;c<NP;c++) sc.append(String.format(Locale.US,"%s%.4f",c==0?"":",",re[11+c][k]/eLN));
      System.out.println(sc);
    }
  }

  static double r7(double f){ return Math.round(f*1e7)/1e7; }

  /** returns {pre, solTag, te0row} or null */
  static Object[] optics(Model m,String lab){
    String[] o1=optStudy(m,"stdO1_"+lab.replaceAll("[^A-Za-z0-9]",""),10,"1.916");
    double[] te=pickTE0(m,o1[1],lab);
    if(te==null) return null;
    String[] o2=optStudy(m,"stdO2_"+lab.replaceAll("[^A-Za-z0-9]",""),1,String.format(Locale.US,"%.6f",te[0]));
    double[] te2=modeRow(m,o2[1],0);
    boolean same=Math.abs(te2[0]-te[0])<1e-6&&te2[3]>0.8;
    double Pw=evalG(m,o2[1],new String[]{"intAll(ewfd.Poavz)"})[0][0];
    System.out.println(String.format(Locale.US,"SOLOPT6F set=%s tag=%s neff=%.8f neff_im=%.4e dBcm=%.4f TEfrac=%.4f ridgeFrac=%.4f same_as_pick=%b P=%.8e W/m xc_um=%.6f",lab,o2[0],te2[0],te2[1],te2[2],te2[3],te2[4],same,Pw,XC*1e6));
    if(!same) return null;
    defineVars(m,o2[0]);
    for(String t:m.sol().tags()) try{ m.sol(t).updateSolution(); }catch(Throwable e){ System.out.println("WARN updateSolution "+t+": "+e.getMessage()); }
    return new Object[]{String.format(Locale.US,"epsilon0_const*c_const/(4*(%.12e))*",Pw),o2[0],te2};
  }

  /** rows: f, PEr, PEi, EOr, EOi, MBr, MBi, ReY, ImY, |tot| */
  static double[][] sweep(Model m,String st,TreeSet<Double> fs,String pre,String sol){
    StringBuilder pl=new StringBuilder();
    for(Double f:fs){ if(pl.length()>0) pl.append(", "); pl.append(String.format(Locale.US,"%.7f[GHz]",f)); }
    Set<String> sb=new HashSet<>(Arrays.asList(m.sol().tags()));
    m.study().create(st);
    m.study(st).create("freq","Frequency");
    m.study(st).feature("freq").set("plist",pl.toString());
    try{ m.study(st).feature("freq").setEntry("activate","ewfd",false); }catch(Throwable t){ System.out.println("WARN deactivate ewfd: "+t.getMessage()); }
    m.study(st).createAutoSequences("all");
    String s=null; for(String t:m.sol().tags()) if(!sb.contains(t)){ s=t; break; }
    System.out.println("STUDY "+st+" sol="+s+" nfreq="+fs.size()+" eta_s="+m.param().get("etas"));
    m.study(st).run();
    String ds="ds_"+st;
    m.result().dataset().create(ds,"Solution");
    m.result().dataset(ds).set("solution",s);
    String[] ex={"freq",pre+"intLN(WPE)",pre+"intLN(WEO)",pre+"("+mbAll("'"+sol+"'")+")","es.Q0_1"};
    double[][][] r=evalGC(m,ds,ex);
    double[][] re=r[0], im=r[1];
    int n=re[0].length;
    double[][] d=new double[n][];
    for(int k=0;k<n;k++){
      double f=re[0][k], w=2*Math.PI*f;
      double reY=-w*im[4][k], imY=w*re[4][k];
      double tr=re[1][k]+re[2][k]+re[3][k], ti=im[1][k]+im[2][k]+im[3][k];
      d[k]=new double[]{f/1e9,re[1][k],im[1][k],re[2][k],im[2][k],re[3][k],im[3][k],reY,imY,Math.hypot(tr,ti)};
      System.out.println(String.format(Locale.US,"F6F set=%s f_GHz=%.6f PE=(%.6e,%.6e) EO=(%.6e,%.6e) MB=(%.6e,%.6e) abs_tot=%.6e ReY_Spm=%.6e ImY_Spm=%.6e",
        st,d[k][0],d[k][1],d[k][2],d[k][3],d[k][4],d[k][5],d[k][6],d[k][9],reY,imY));
    }
    try{ m.sol(s).clearSolutionData(); }catch(Throwable t){ System.out.println("WARN clearSolutionData "+s+": "+t.getMessage()); }
    return d;
  }

  /** returns {f, |tot|, Q, ReY, ImY} */
  static double[] peak(double[][] d0,String lab,boolean print){
    double[][] d=d0.clone();
    Arrays.sort(d,(x,y)->Double.compare(x[0],y[0]));
    int n=d.length, ip=0;
    for(int k=0;k<n;k++) if(d[k][9]>d[ip][9]) ip=k;
    double h=d[ip][9]/Math.sqrt(2), lo=Double.NaN, hi=Double.NaN;
    for(int j=ip;j>0;j--) if(d[j-1][9]<h){ lo=d[j-1][0]+(h-d[j-1][9])*(d[j][0]-d[j-1][0])/(d[j][9]-d[j-1][9]); break; }
    for(int j=ip;j<n-1;j++) if(d[j+1][9]<h){ hi=d[j][0]+(h-d[j][9])*(d[j+1][0]-d[j][0])/(d[j+1][9]-d[j][9]); break; }
    double Q=d[ip][0]/(hi-lo);
    boolean edge=ip==0||ip==n-1;
    System.out.println(String.format(Locale.US,"PEAK6F set=%s f_peak_GHz=%.6f abs_tot_peak=%.6e FWHM_MHz=%.4f Q=%.1f PE=(%.6e,%.6e) EO=(%.6e,%.6e) MB=(%.6e,%.6e) ReY_Spm=%.6e ImY_Spm=%.6e at_edge=%b",
      lab,d[ip][0],d[ip][9],(hi-lo)*1e3,Q,d[ip][1],d[ip][2],d[ip][3],d[ip][4],d[ip][5],d[ip][6],d[ip][7],d[ip][8],edge));
    int iy=0; for(int k=0;k<n;k++) if(d[k][7]>d[iy][7]) iy=k;
    System.out.println(String.format(Locale.US,"REY6F set=%s f_maxReY_GHz=%.6f ReY_max_Spm=%.6e",lab,d[iy][0],d[iy][7]));
    return new double[]{d[ip][0],d[ip][9],Q,d[ip][7],d[ip][8]};
  }

  static void eigen(Model m,int[][] G,double[] mainPk,double[] lowPk){
    m.component("comp1").physics("es").feature("term1").active(false);
    m.component("comp1").physics("es").create("gndT","Ground",1); m.component("comp1").physics("es").feature("gndT").selection().set(G[0]);
    m.study().create("stdE"); m.study("stdE").create("eig","Eigenfrequency");
    m.study("stdE").feature("eig").set("neigs","40");
    m.study("stdE").feature("eig").set("shift","3.33[GHz]");
    m.study("stdE").feature("eig").set("shiftactive","on");
    try{ m.study("stdE").feature("eig").setEntry("activate","ewfd",false); }catch(Throwable t){ System.out.println("WARN deactivate ewfd eig: "+t.getMessage()); }
    Set<String> sb=new HashSet<>(Arrays.asList(m.sol().tags()));
    m.study("stdE").createAutoSequences("all");
    String s=null; for(String t:m.sol().tags()) if(!sb.contains(t)){ s=t; break; }
    System.out.println("STUDY stdE sol="+s+" neigs=40 shift=3.33GHz (term1 off, term edges grounded)");
    m.study("stdE").run();
    m.result().dataset().create("ds_stdE","Solution");
    m.result().dataset("ds_stdE").set("solution",s);
    List<String> ex=new ArrayList<>();
    ex.add("freq");
    ex.add("intLN(solid.Ws)"); ex.add("intAl(solid.Ws)");
    ex.add("intLN(abs(u)^2)"); ex.add("intLN(abs(v)^2)"); ex.add("intLN(abs(w)^2)");
    ex.add("intLN(abs(v)^2*(x>="+ID+"*p)*(x<"+(ID+1)+"*p))");
    ex.add("intBotB(abs(v)^2)");
    for(int k=-NH;k<=NH;k++) ex.add("intBotB(v*exp(-i*2*pi*("+k+")*x/p))");
    double[][][] r=evalGC(m,"ds_stdE",ex.toArray(new String[0]));
    double[][] re=r[0], im=r[1];
    int nm=re[0].length;
    double scale=(double)(NP-DEF.length)/NP;
    System.out.println(String.format(Locale.US,"EIGREF6F expect_fracAl_driven=%.4f partner=%.4f (unit x %d/%d); 6d-2 V2 target 3.340627 GHz fracAl~0.0485 Pfrac 0.973",FA_T_UNIT*scale,FA_P_UNIT*scale,NP-DEF.length,NP));
    double[] fA=new double[nm], pvA=new double[nm], faA=new double[nm], pfA=new double[nm];
    for(int k=0;k<nm;k++){
      double f=re[0][k]/1e9, fi=im[0][k]/1e9;
      double eL=Math.abs(re[1][k]), eA=Math.abs(re[2][k]);
      double ut=re[3][k]+re[4][k]+re[5][k];
      double pv=ut>0?re[4][k]/ut:-1, fracAl=(eL+eA)>0?eA/(eL+eA):-1;
      double defect=re[4][k]>0?re[6][k]/(re[4][k]/NP):-1;
      double sc=0; for(int j=0;j<2*NH+1;j++){ double a=re[8+j][k], b=im[8+j][k]; sc+=a*a+b*b; }
      double pfrac=re[7][k]>0?sc/(LS*re[7][k]):-1;
      double q=fi!=0?f/(2*Math.abs(fi)):-1;
      fA[k]=f; pvA[k]=pv; faA[k]=fracAl; pfA[k]=pfrac;
      String tag=(f>=3.29&&f<=3.36)?"EIG6F":"EIG6F_OUT";
      System.out.println(String.format(Locale.US,"%s k=%d f_GHz=%.6f Q=%.1f pv=%.3f fracAl=%.4f Pfrac=%.4f defectRatio=%.3f",tag,k,f,q,pv,fracAl,pfrac,defect));
    }
    for(Object[] pk:new Object[][]{{"MAIN",mainPk},{"LOW",lowPk}}){
      double[] q=(double[])pk[1]; if(q==null) continue;
      int b=-1;
      for(int k=0;k<nm;k++){ if(pvA[k]<0.5||pfA[k]<0.3) continue; if(b<0||Math.abs(fA[k]-q[0])<Math.abs(fA[b]-q[0])) b=k; }
      if(b<0){ System.out.println("MATCH6F set="+pk[0]+" NONE"); continue; }
      System.out.println(String.format(Locale.US,"MATCH6F set=%s f_drive_GHz=%.6f nearest_eig k=%d f_GHz=%.6f df_MHz=%.3f pv=%.3f fracAl=%.4f Pfrac=%.4f",pk[0],q[0],b,fA[b],(fA[b]-q[0])*1e3,pvA[b],faA[b],pfA[b]));
    }
  }

  static String mbH(String s){
    return String.format(Locale.US,"%.10f*abs(withsol(%s,ewfd.Ex))^2+%.10f*abs(withsol(%s,ewfd.Ez))^2+%.10f*abs(withsol(%s,ewfd.Dy)/epsilon0_const)^2",
      NO*NO-1,s,NEX*NEX-1,s,1-1/(NO*NO),s);
  }
  static String mbV(String s){
    return String.format(Locale.US,"%.10f*abs(withsol(%s,ewfd.Ey))^2+%.10f*abs(withsol(%s,ewfd.Ez))^2+%.10f*abs(withsol(%s,ewfd.Dx)/epsilon0_const)^2",
      NO*NO-1,s,NEX*NEX-1,s,1-1/(NO*NO),s);
  }
  static String mbAll(String s){
    return "intTopB(v*("+mbH(s)+"))+intBotB(-v*("+mbH(s)+"))+intWallL(-u*("+mbV(s)+"))+intWallR(u*("+mbV(s)+"))";
  }

  static void defineVars(Model m,String sol){
    String s="'"+sol+"'";
    double eO=NO*NO, eE=NEX*NEX;
    String[][] v={
      {"Ox","withsol("+s+",ewfd.Ex)"},{"Oy","withsol("+s+",ewfd.Ey)"},{"Oz","withsol("+s+",ewfd.Ez)"},
      {"S1","solid.eYY"},{"S2","solid.eXX"},{"S3","solid.eZZ"},{"S4","-2*solid.eXZ"},{"S5","2*solid.eYZ"},{"S6","-2*solid.eXY"},
      {"Ec1","es.Ey"},{"Ec2","-es.Ex"},
      {"p11","-0.026"},{"p12","0.090"},{"p13","0.133"},{"p14","-0.075"},{"p31","0.179"},{"p33","0.071"},{"p41","-0.151"},{"p44","0.146"},
      {"r22","3.4e-12[m/V]"},{"r51","28e-12[m/V]"},
      {"dP1","p11*S1+p12*S2+p13*S3+p14*S4"},{"dP2","p12*S1+p11*S2+p13*S3-p14*S4"},{"dP3","p31*(S1+S2)+p33*S3"},
      {"dP4","p41*S1-p41*S2+p44*S4"},{"dP5","p44*S5+p41*S6"},{"dP6","p14*S5+(p11-p12)/2*S6"},
      {"dE1","-r22*Ec2"},{"dE2","r22*Ec2"},{"dE3","0"},{"dE4","r51*Ec2"},{"dE5","r51*Ec1"},{"dE6","-r22*Ec1"},
      {"eX",fs(eO)},{"eY",fs(eO)},{"eZ",fs(eE)}
    };
    m.component("comp1").variable().create("vPert");
    m.component("comp1").variable("vPert").selection().geom("geom1",2);
    m.component("comp1").variable("vPert").selection().named("selLN");
    for(String[] kv:v) m.component("comp1").variable("vPert").set(kv[0],kv[1]);
    for(String t:new String[]{"P","E"}){
      String d=t.equals("P")?"dP":"dE";
      String xx="(-eX*eX*"+d+"2)", yy="(-eY*eY*"+d+"1)", zz="(-eZ*eZ*"+d+"3)", xy="(-eX*eY*(-"+d+"6))", xz="(-eX*eZ*(-"+d+"4))", yz="(-eY*eZ*"+d+"5)";
      m.component("comp1").variable("vPert").set("W"+t+(t.equals("P")?"E":"O"),
        xx+"*abs(Ox)^2+"+yy+"*abs(Oy)^2+"+zz+"*abs(Oz)^2+2*("+xy+"*realdot(Ox,Oy)+"+xz+"*realdot(Ox,Oz)+"+yz+"*realdot(Oy,Oz))");
    }
  }
  static String fs(double v){ return String.format(Locale.US,"%.10f",v); }

  static int[][] build(Model m,double hR,boolean acoustic)throws Exception{
    m.param().set("p",String.format(Locale.US,"%.10f[um]",P_UM));
    m.param().set("dnL","0");
    m.param().set("etas","5e-4");
    m.component().create("comp1",true);
    GeomSequence g=m.component("comp1").geom().create("geom1",2);
    g.lengthUnit("m");
    rect(g,"airB",0,-HAIR,LS,HAIR);
    rect(g,"airT",0,HLN,LS,HAIR);
    rect(g,"rLn",0,0,LS,HLN);
    rect(g,"rRg",XC-WR/2,HLN,WR,hR);
    int nf=0;
    for(int c=0;c<NP;c++){
      if(isDef(c)) continue;
      rect(g,"rAp"+c,c*P+0.125*P,HLN,0.25*P,HAL);
      rect(g,"rAn"+c,c*P+0.625*P,HLN,0.25*P,HAL);
      nf+=2;
    }
    g.run();
    box(m,"selSlab",2,-1e-9,LS+1e-9,-1e-9,HLN+1e-9);
    box(m,"selRidge",2,XC-WR/2-1e-9,XC+WR/2+1e-9,HLN-1e-9,HLN+hR+1e-9);
    union(m,"selLN",new String[]{"selSlab","selRidge"});
    box(m,"selAlL",2,-1e-9,XC-WR/2-1e-9,HLN-1e-9,HLN+HAL+1e-9);
    box(m,"selAlR",2,XC+WR/2+1e-9,LS+1e-9,HLN-1e-9,HLN+HAL+1e-9);
    union(m,"selAl",new String[]{"selAlL","selAlR"});
    int[][] G=classify(m,g,hR);
    int nLN=ents(m,"selLN").length, nAl=ents(m,"selAl").length;
    System.out.println(String.format(Locale.US,"GEOM6F xc_um=%.6f hR_nm=%.0f nDom=%d nLN=%d(exp 2) nAl=%d(exp %d) nTerm=%d nGnd=%d(exp %d) nTopB=%d nBotB=%d nWallL=%d nWallR=%d nRidgeTop=%d nExt=%d nSideLN=%d",
      XC*1e6,hR*1e9,g.getNDomains(),nLN,nAl,nf,G[0].length,G[1].length,nf/2,G[2].length,G[3].length,G[4].length,G[5].length,G[6].length,G[7].length,G[8].length));
    if(nLN!=2||nAl!=nf||G[0].length!=nf/2||G[1].length!=nf/2||G[4].length<1||G[5].length<1||G[6].length<1||G[3].length<1) throw new RuntimeException("selection mismatch");

    if(acoustic){
      Model pz=ModelUtil.load("pz",PZ); Model bs=ModelUtil.load("basic",BASIC);
      Material ln=m.component("comp1").material().create("matLN","Common"); ln.selection().named("selLN");
      copyGroup(ln,pz.material("lithium_niobate"),"def",false); copyGroup(ln,pz.material("lithium_niobate"),"StressCharge",true);
      Material al=m.component("comp1").material().create("matAl","Common"); al.selection().named("selAl");
      copyGroup(al,bs.material("aluminum"),"def",false); copyGroup(al,bs.material("aluminum"),"Enu",true);
      ModelUtil.remove("pz"); ModelUtil.remove("basic");
      union(m,"selSolid",new String[]{"selLN","selAl"});
      m.component("comp1").physics().create("solid","SolidMechanics","geom1");
      m.component("comp1").physics("solid").selection().named("selSolid");
      m.component("comp1").physics().create("es","Electrostatics","geom1");
      m.component("comp1").physics("es").selection().named("selLN");
      m.component("comp1").physics("solid").create("pzm1","PiezoelectricMaterialModel",2); m.component("comp1").physics("solid").feature("pzm1").selection().named("selLN");
      m.component("comp1").multiphysics().create("pze1","PiezoelectricEffect","geom1");
      m.component("comp1").physics("es").create("ccp1","ChargeConservationPiezo",2); m.component("comp1").physics("es").feature("ccp1").selection().named("selLN");
      Object sys=m.component("comp1").coordSystem().create("sys2","Rotated"); sS(sys,"rotationSequence","ZXZ"); sA(sys,"angle",new String[]{"90[deg]","0","0"});
      sS(m.component("comp1").physics("solid").feature("pzm1"),"coordinateSystem","sys2"); sS(m.component("comp1").physics("es").feature("ccp1"),"coordinateSystem","sys2");
      m.component("comp1").physics("solid").feature("pzm1").create("dmp1","Damping",2);
      m.component("comp1").physics("solid").feature("pzm1").feature("dmp1").set("DampingType","IsotropicLossFactor");
      m.component("comp1").physics("solid").feature("pzm1").feature("dmp1").set("eta_s_mat","userdef");
      m.component("comp1").physics("solid").feature("pzm1").feature("dmp1").set("eta_s","etas");
      m.component("comp1").physics("es").create("term1","Terminal",1); m.component("comp1").physics("es").feature("term1").selection().set(G[0]);
      m.component("comp1").physics("es").feature("term1").set("TerminalType","Voltage");
      m.component("comp1").physics("es").feature("term1").set("V0","1[V]");
      m.component("comp1").physics("es").create("gnd1","Ground",1); m.component("comp1").physics("es").feature("gnd1").selection().set(G[1]);
      m.component("comp1").physics("solid").create("pc1","PeriodicCondition",1); m.component("comp1").physics("solid").feature("pc1").selection().set(G[8]);
      m.component("comp1").physics("es").create("pc1","PeriodicCondition",1); m.component("comp1").physics("es").feature("pc1").selection().set(G[8]);
      Object pr=m.component("comp1").physics("solid").prop("Type2D"); sS(pr,"ModeExtension","1"); sS(pr,"kz","0");
    }

    m.component("comp1").physics().create("ewfd","ElectromagneticWavesFrequencyDomain","geom1");
    Object w1=m.component("comp1").physics("ewfd").feature("wee1");
    sS(w1,"DisplacementFieldModel","RelativePermittivity");
    sS(w1,"epsilonr_mat","userdef"); sA(w1,"epsilonr",new String[]{"1","0","0","0","1","0","0","0","1"});
    sS(w1,"mur_mat","userdef"); sA(w1,"mur",new String[]{"1","0","0","0","1","0","0","0","1"});
    sS(w1,"sigma_mat","userdef"); sA(w1,"sigma",new String[]{"0","0","0","0","0","0","0","0","0"});
    m.component("comp1").physics("ewfd").create("weeLN","WaveEquationElectric",2);
    m.component("comp1").physics("ewfd").feature("weeLN").selection().named("selLN");
    Object w2=m.component("comp1").physics("ewfd").feature("weeLN");
    sS(w2,"DisplacementFieldModel","RelativePermittivity");
    String o2="("+NO+"+dnL)^2", e2="("+NEX+"+dnL)^2";
    sS(w2,"epsilonr_mat","userdef"); sA(w2,"epsilonr",new String[]{o2,"0","0","0",o2,"0","0","0",e2});
    sS(w2,"mur_mat","userdef"); sA(w2,"mur",new String[]{"1","0","0","0","1","0","0","0","1"});
    sS(w2,"sigma_mat","userdef"); sA(w2,"sigma",new String[]{"0","0","0","0","0","0","0","0","0"});
    m.component("comp1").physics("ewfd").create("weeAl","WaveEquationElectric",2);
    m.component("comp1").physics("ewfd").feature("weeAl").selection().named("selAl");
    Object w3=m.component("comp1").physics("ewfd").feature("weeAl");
    sS(w3,"DisplacementFieldModel","RefractiveIndex");
    sS(w3,"n_mat","userdef"); sA(w3,"n",new String[]{""+N_AL,"0","0","0",""+N_AL,"0","0","0",""+N_AL});
    sS(w3,"ki_mat","userdef"); sA(w3,"ki",new String[]{""+K_AL,"0","0","0",""+K_AL,"0","0","0",""+K_AL});
    m.component("comp1").physics("ewfd").create("sctr1","Scattering",1);
    m.component("comp1").physics("ewfd").feature("sctr1").selection().set(G[7]);

    cpl(m,"intAll",2,null); cpl(m,"intLN",2,"selLN"); cpl(m,"intAl",2,"selAl");
    cplE(m,"intTopB",G[2]); cplE(m,"intBotB",G[3]); cplE(m,"intWallL",G[4]); cplE(m,"intWallR",G[5]); cplE(m,"intRTop",G[6]);
    m.param().set("xc",String.format(Locale.US,"%.10e[m]",XC));

    m.component("comp1").mesh().create("mesh1");
    m.component("comp1").mesh("mesh1").feature("size").set("custom","on");
    m.component("comp1").mesh("mesh1").feature("size").set("hmax","150[nm]");
    m.component("comp1").mesh("mesh1").feature("size").set("hmin","1[nm]");
    msize(m,"szLN","selLN","30[nm]");
    msize(m,"szAl","selAl","10[nm]");
    m.component("comp1").mesh("mesh1").create("ftri1","FreeTri");
    m.component("comp1").mesh("mesh1").run();
    System.out.println(String.format(Locale.US,"NUMELEM6F xc_um=%.6f n_elem=%d",XC*1e6,m.component("comp1").mesh("mesh1").getNumElem()));
    return G;
  }

  static int[][] classify(Model m,GeomSequence g,double hR){
    double tol=1e-11, a=0.125*P, w=0.25*P;
    List<Integer> term=new ArrayList<>(),gnd=new ArrayList<>(),top=new ArrayList<>(),bot=new ArrayList<>(),wl=new ArrayList<>(),wr=new ArrayList<>(),rt=new ArrayList<>(),ext=new ArrayList<>(),side=new ArrayList<>();
    int nE=g.getNEdges();
    for(int e=1;e<=nE;e++){
      double[][] q=g.edgeX(e,new double[]{0.0,0.5,1.0});
      double x0=q[0][0],y0=q[0][1],xm=q[1][0],ym=q[1][1],x1=q[2][0],y1=q[2][1];
      boolean hor=Math.abs(y0-y1)<tol, ver=Math.abs(x0-x1)<tol;
      double len=Math.hypot(x1-x0,y1-y0);
      if(ver&&(Math.abs(xm)<tol||Math.abs(xm-LS)<tol)){ ext.add(e); if(ym>0&&ym<HLN) side.add(e); continue; }
      if(hor&&(Math.abs(ym+HAIR)<tol||Math.abs(ym-HLN-HAIR)<tol)){ ext.add(e); continue; }
      if(hor&&Math.abs(ym)<tol){ bot.add(e); continue; }
      if(hor&&Math.abs(ym-HLN)<tol){
        int c=(int)Math.floor(xm/P);
        double xr=xm-c*P;
        if(!isDef(c)&&Math.abs(len-w)<1e-10&&xr>a&&xr<a+w){ term.add(e); continue; }
        if(!isDef(c)&&Math.abs(len-w)<1e-10&&xr>P/2+a&&xr<P/2+a+w){ gnd.add(e); continue; }
        if(xm>XC-WR/2&&xm<XC+WR/2) continue;
        top.add(e); continue;
      }
      if(hor&&Math.abs(ym-HLN-hR)<tol&&xm>XC-WR/2&&xm<XC+WR/2){ top.add(e); rt.add(e); continue; }
      if(ver&&Math.abs(xm-(XC-WR/2))<tol&&ym>HLN&&ym<HLN+hR){ wl.add(e); continue; }
      if(ver&&Math.abs(xm-(XC+WR/2))<tol&&ym>HLN&&ym<HLN+hR){ wr.add(e); continue; }
    }
    int[][] G=new int[9][];
    G[0]=ia(term); G[1]=ia(gnd); G[2]=ia(top); G[3]=ia(bot); G[4]=ia(wl); G[5]=ia(wr); G[6]=ia(rt); G[7]=ia(ext); G[8]=ia(side);
    return G;
  }

  static String[] optStudy(Model m,String st,int neigs,String shift){
    Set<String> sb=new HashSet<>(Arrays.asList(m.sol().tags()));
    m.study().create(st);
    m.study(st).create("mode","ModeAnalysis");
    m.study(st).feature("mode").set("modeFreq","c_const/1.55[um]");
    m.study(st).feature("mode").set("neigsactive",true);
    m.study(st).feature("mode").set("neigs",neigs);
    m.study(st).feature("mode").set("shiftactive",true);
    m.study(st).feature("mode").set("shift",shift);
    for(String ph:new String[]{"solid","es","pze1"}) try{ m.study(st).feature("mode").setEntry("activate",ph,false); }catch(Throwable t){}
    m.study(st).createAutoSequences("all");
    String sol=null; for(String t:m.sol().tags()) if(!sb.contains(t)){ sol=t; break; }
    for(String ft:m.sol(sol).feature().tags()){
      if(!ft.startsWith("e")) continue;
      try{
        if("outofplanewavenumber".equals(m.sol(sol).feature(ft).getString("transform")))
          m.sol(sol).feature(ft).set("shift",String.format(Locale.US,"%.10e",Double.parseDouble(shift)*K0));
        m.sol(sol).feature(ft).set("neigs",String.valueOf(neigs));
      }catch(Throwable t){ System.out.println("EIGFEAT_WARN "+ft+" "+t.getMessage()); }
    }
    m.study(st).run();
    String ds="ds_"+st;
    m.result().dataset().create(ds,"Solution");
    m.result().dataset(ds).set("solution",sol);
    System.out.println("STUDY "+st+" sol="+sol+" dataset="+ds+" neigs="+neigs+" shift_neff="+shift);
    return new String[]{sol,ds};
  }

  static double[] modeRow(Model m,String ds,int k){
    double[][] v=evalG(m,ds,new String[]{"real(ewfd.neff)","imag(ewfd.neff)","intAll(abs(ewfd.Ex)^2)","intAll(ewfd.normE^2)","intAll(ewfd.normE^2*(abs(x-xc)<0.5[um]))"});
    return new double[]{v[0][k],v[1][k],8.686*K0*Math.abs(v[1][k])/100,v[2][k]/v[3][k],v[4][k]/v[3][k]};
  }
  static double[] pickTE0(Model m,String ds,String lab){
    double[][] v=evalG(m,ds,new String[]{"real(ewfd.neff)","imag(ewfd.neff)","intAll(abs(ewfd.Ex)^2)","intAll(ewfd.normE^2)","intAll(ewfd.normE^2*(abs(x-xc)<0.5[um]))"});
    double[] best=null;
    for(int k=0;k<v[0].length;k++){
      double te=v[2][k]/v[3][k], rf=v[4][k]/v[3][k], db=8.686*K0*Math.abs(v[1][k])/100;
      System.out.println(String.format(Locale.US,"MODE6F set=%s k=%d neff_re=%.6f neff_im=%.4e dBcm=%.4f TEfrac=%.4f ridgeFrac=%.4f",lab,k,v[0][k],v[1][k],db,te,rf));
      if(te>0.8&&(best==null||rf>best[4])) best=new double[]{v[0][k],v[1][k],db,te,rf};
    }
    if(best!=null&&best[4]<0.3) best=null;
    return best;
  }

  static double[][] evalG(Model m,String ds,String[] ex){ return evalGC(m,ds,ex)[0]; }
  static double[][][] evalGC(Model m,String ds,String[] ex){
    m.result().numerical().create("gq","EvalGlobal");
    m.result().numerical("gq").set("data",ds);
    m.result().numerical("gq").set("expr",ex);
    m.result().numerical("gq").set("looplevelinput",new String[]{"all"});
    double[][] re=m.result().numerical("gq").getReal();
    double[][] im=m.result().numerical("gq").getImag();
    m.result().numerical().remove("gq");
    return new double[][][]{re,im};
  }

  static boolean isDef(int c){ for(int d:DEF) if(d==c) return true; return false; }
  static int[] ia(List<Integer> l){ int[] r=new int[l.size()]; for(int i=0;i<r.length;i++) r[i]=l.get(i); return r; }
  static int[] ents(Model m,String s){ return m.component("comp1").selection(s).entities(); }
  static void rect(GeomSequence g,String t,double x,double y,double w,double h){
    g.create(t,"Rectangle");
    g.feature(t).set("size",new String[]{String.format(Locale.US,"%.12e",w),String.format(Locale.US,"%.12e",h)});
    g.feature(t).set("pos",new String[]{String.format(Locale.US,"%.12e",x),String.format(Locale.US,"%.12e",y)});
  }
  static void box(Model m,String t,int dim,double xa,double xb,double ya,double yb){
    m.component("comp1").selection().create(t,"Box");
    m.component("comp1").selection(t).set("entitydim",""+dim);
    m.component("comp1").selection(t).set("condition","inside");
    m.component("comp1").selection(t).set("xmin",String.format(Locale.US,"%.12e",xa)); m.component("comp1").selection(t).set("xmax",String.format(Locale.US,"%.12e",xb));
    m.component("comp1").selection(t).set("ymin",String.format(Locale.US,"%.12e",ya)); m.component("comp1").selection(t).set("ymax",String.format(Locale.US,"%.12e",yb));
  }
  static void union(Model m,String t,String[] in){
    m.component("comp1").selection().create(t,"Union");
    m.component("comp1").selection(t).set("entitydim","2");
    m.component("comp1").selection(t).set("input",in);
  }
  static void cpl(Model m,String t,int dim,String sel){
    m.component("comp1").cpl().create(t,"Integration");
    m.component("comp1").cpl(t).selection().geom("geom1",dim);
    if(sel==null) m.component("comp1").cpl(t).selection().all(); else m.component("comp1").cpl(t).selection().named(sel);
  }
  static void cplE(Model m,String t,int[] e){
    m.component("comp1").cpl().create(t,"Integration");
    m.component("comp1").cpl(t).selection().geom("geom1",1);
    m.component("comp1").cpl(t).selection().set(e);
  }
  static void msize(Model m,String t,String sel,String h){
    m.component("comp1").mesh("mesh1").create(t,"Size");
    m.component("comp1").mesh("mesh1").feature(t).selection().geom("geom1",2);
    m.component("comp1").mesh("mesh1").feature(t).selection().named(sel);
    m.component("comp1").mesh("mesh1").feature(t).set("custom","on");
    m.component("comp1").mesh("mesh1").feature(t).set("hmaxactive",true);
    m.component("comp1").mesh("mesh1").feature(t).set("hmax",h);
  }
  static void copyGroup(Material d,Material s,String g,boolean c){
    if(c) d.propertyGroup().create(g,g);
    String[] n=s.propertyGroup(g).properties();
    for(int i=0;i<n.length;i++){ try{ d.propertyGroup(g).set(n[i],s.propertyGroup(g).getStringArray(n[i])); }catch(Exception e){} }
  }
  static void sS(Object o,String n,String v)throws Exception{ o.getClass().getMethod("set",String.class,String.class).invoke(o,n,v); }
  static void sA(Object o,String n,String[] v)throws Exception{ o.getClass().getMethod("set",String.class,String[].class).invoke(o,n,v); }
}
