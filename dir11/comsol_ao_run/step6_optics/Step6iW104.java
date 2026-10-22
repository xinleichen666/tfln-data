import com.comsol.model.*;
import com.comsol.model.util.*;
import java.util.*;
import java.util.Locale;

/** Step 6i: calibration against Shao et al., Optica 6, 1498 (2019). Suspended X-cut LN, 0.8 um film, 0.4 um rib etch,
 *  0.95 um top width, 70 deg sidewalls, 4 Au fingers (75 nm). Sim x = crystal Z, sim y = crystal X, propagation = crystal Y.
 *  Eigenmodes: single-phonon index change (Shao Eq. S1/S6) and VpiL from Shao Eq. S10 (Q=2000, ge/g=0.15, 50 ohm).
 *  Driven: |dneff|/V and Y around the strongest modes. Geometry widths from Shao Fig. 2(c) pixels (20 px/um). */
public class Step6iW104 {
  static final String PZ="D:\\COMSOL63\\Multiphysics\\data\\comsol_piezo_lib.mph";
  static final String BASIC="D:\\COMSOL63\\Multiphysics\\data\\comsol_basic_material_lib.mph";
  static final String MEMS="D:\\COMSOL63\\Multiphysics\\data\\comsol_mems_lib.mph";
  static final String CASE="W104";
  static final double HS=400e-9, HR=400e-9, WT=0.95e-6, ANG=70.0, HAU=75e-9, WF=0.375e-6, PF=0.64e-6, HAIR=2e-6, XAIR=1e-6;
  static final double NO=2.211, NEX=2.138, N_AU=0.56, K_AU=11.2, LAM=1.55e-6, K0=2*Math.PI/LAM;
  static final double HBAR=1.054571817e-34, LA=100e-6, QS=2000, GE=0.15, RIN=50;
  static double W=10.4e-6, XR=2.6e-6, XF0=5.875e-6;
  static boolean ESAIR=false;
  static double WB(){ return WT/2+HR/Math.tan(Math.toRadians(ANG)); }

  public static void main(String[] args){
    try{
      ModelUtil.initStandalone(true);
      if(CASE.equals("W104")){ W=10.4e-6; XR=2.6e-6; XF0=5.875e-6; }
      else if(CASE.equals("W099")){ W=9.9e-6; XR=2.5e-6; XF0=5.6e-6; }
      else if(CASE.equals("W104A")){ W=10.4e-6; XR=2.6e-6; XF0=5.875e-6; ESAIR=true; }
      else throw new RuntimeException("unknown case "+CASE);
      System.out.println("STEP6I_START case="+CASE);
      System.out.println(String.format(Locale.US,"CFG6I case=%s W_um=%.3f XR_um=%.3f rib_top_um=%.3f rib_bot_um=%.4f HS_nm=%.0f HR_nm=%.0f Au_nm=%.0f finger_w_um=%.3f finger_pitch_um=%.3f XF_um=%.3f..%.3f eta_s=5e-4 La_um=100",
        CASE,W*1e6,XR*1e6,WT*1e6,2*WB()*1e6,HS*1e9,HR*1e9,HAU*1e9,WF*1e6,PF*1e6,XF0*1e6,(XF0+3*PF)*1e6));
      Model m=ModelUtil.create("M6i");
      int[][] G=build(m);
      Object[] op=optics(m);
      if(op==null){ System.out.println("STEP6I_STOP no TE0"); return; }
      String pre=(String)op[0], SOL=(String)op[1];
      orientCheck(m);
      List<double[]> top=eigen(m,G,pre,SOL);
      m.component("comp1").physics("es").feature("gndT").active(false);
      m.component("comp1").physics("es").feature("term1").active(true);
      int ip=0;
      for(double[] t:top){
        TreeSet<Double> fs=new TreeSet<>();
        for(int i=-24;i<=24;i++) fs.add(r7(t[0]+0.00025*i));
        double[][] d=sweep(m,"stdF"+ip,fs,pre,SOL);
        peak(d,CASE+"_m"+(int)t[1],t);
        ip++;
      }
      ModelUtil.remove("M6i");
      System.out.println("STEP6I_DONE case="+CASE);
    }catch(Throwable t){ System.out.println("STEP6I_ABORT"); t.printStackTrace(System.out); }
  }

  static double r7(double f){ return Math.round(f*1e7)/1e7; }

  static Object[] optics(Model m){
    String[] o1=optStudy(m,"stdO1",10,"1.95");
    double[] te=pickTE0(m,o1[1]);
    if(te==null) return null;
    String[] o2=optStudy(m,"stdO2",1,String.format(Locale.US,"%.6f",te[0]));
    double[] te2=modeRow(m,o2[1],0);
    boolean same=Math.abs(te2[0]-te[0])<1e-6&&te2[3]>0.8;
    double Pw=evalG(m,o2[1],new String[]{"intAll(ewfd.Poavz)"})[0][0];
    System.out.println(String.format(Locale.US,"SOLOPT6I case=%s tag=%s neff=%.8f neff_im=%.4e dBcm=%.4f TEfrac=%.4f ribFrac=%.4f same_as_pick=%b P=%.8e W/m",CASE,o2[0],te2[0],te2[1],te2[2],te2[3],te2[4],same,Pw));
    if(!same) return null;
    defineVars(m,o2[0]);
    for(String t:m.sol().tags()) try{ m.sol(t).updateSolution(); }catch(Throwable e){ System.out.println("WARN updateSolution "+t+": "+e.getMessage()); }
    return new Object[]{String.format(Locale.US,"epsilon0_const*c_const/(4*(%.12e))*",Pw),o2[0]};
  }

  static void orientCheck(Model m){
    String[] names={"es.epsilonrxx","es.epsilonryy","es.epsilonrzz","solid.epsilonrSxx","solid.epsilonrSyy"};
    for(String n:names){
      try{
        m.result().numerical().create("ev","EvalGlobal");
        m.result().numerical("ev").set("expr",new String[]{"intLN("+n+")/intLN(1)"});
        double v=m.result().numerical("ev").getReal()[0][0];
        System.out.println(String.format(Locale.US,"ORIENT6I %s=%.4f",n,v));
      }catch(Throwable t){ System.out.println("ORIENT6I "+n+" n/a"); }
      try{ m.result().numerical().remove("ev"); }catch(Throwable t){}
    }
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
    System.out.println("STUDY "+st+" sol="+s+" nfreq="+fs.size());
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
      System.out.println(String.format(Locale.US,"F6I set=%s f_GHz=%.6f PE=(%.6e,%.6e) EO=(%.6e,%.6e) MB=(%.6e,%.6e) abs_tot=%.6e ReY_Spm=%.6e ImY_Spm=%.6e",
        st,d[k][0],d[k][1],d[k][2],d[k][3],d[k][4],d[k][5],d[k][6],d[k][9],reY,imY));
    }
    try{ m.sol(s).clearSolutionData(); }catch(Throwable t){ System.out.println("WARN clearSolutionData "+s+": "+t.getMessage()); }
    return d;
  }

  static void peak(double[][] d0,String lab,double[] eg){
    double[][] d=d0.clone();
    Arrays.sort(d,(x,y)->Double.compare(x[0],y[0]));
    int n=d.length, ip=0;
    for(int k=0;k<n;k++) if(d[k][9]>d[ip][9]) ip=k;
    double h=d[ip][9]/Math.sqrt(2), lo=Double.NaN, hi=Double.NaN;
    for(int j=ip;j>0;j--) if(d[j-1][9]<h){ lo=d[j-1][0]+(h-d[j-1][9])*(d[j][0]-d[j-1][0])/(d[j][9]-d[j-1][9]); break; }
    for(int j=ip;j<n-1;j++) if(d[j+1][9]<h){ hi=d[j][0]+(h-d[j][9])*(d[j+1][0]-d[j][0])/(d[j+1][9]-d[j][9]); break; }
    double Q=d[ip][0]/(hi-lo);
    System.out.println(String.format(Locale.US,"PEAK6I set=%s eig_f_GHz=%.6f f_peak_GHz=%.6f abs_tot_peak=%.6e FWHM_MHz=%.4f Q=%.1f PE=(%.6e,%.6e) EO=(%.6e,%.6e) MB=(%.6e,%.6e) ReY_Spm=%.6e ImY_Spm=%.6e at_edge=%b",
      lab,eg[0],d[ip][0],d[ip][9],(hi-lo)*1e3,Q,d[ip][1],d[ip][2],d[ip][3],d[ip][4],d[ip][5],d[ip][6],d[ip][7],d[ip][8],ip==0||ip==n-1));
  }

  /** eigenmodes with single-phonon index change; returns the 4 strongest modes {f_GHz, k} in 1.4-3.6 GHz */
  static List<double[]> eigen(Model m,int[][] G,String pre,String sol){
    m.component("comp1").physics("es").feature("term1").active(false);
    m.component("comp1").physics("es").create("gndT","Ground",1); m.component("comp1").physics("es").feature("gndT").selection().set(TERM(G));
    m.study().create("stdE"); m.study("stdE").create("eig","Eigenfrequency");
    m.study("stdE").feature("eig").set("neigs","100");
    m.study("stdE").feature("eig").set("shift","2.5[GHz]");
    m.study("stdE").feature("eig").set("shiftactive","on");
    try{ m.study("stdE").feature("eig").setEntry("activate","ewfd",false); }catch(Throwable t){ System.out.println("WARN deactivate ewfd eig: "+t.getMessage()); }
    Set<String> sb=new HashSet<>(Arrays.asList(m.sol().tags()));
    m.study("stdE").createAutoSequences("all");
    String s=null; for(String t:m.sol().tags()) if(!sb.contains(t)){ s=t; break; }
    System.out.println("STUDY stdE sol="+s+" neigs=100 shift=2.5GHz (term1 off, term edges grounded)");
    m.study("stdE").run();
    m.result().dataset().create("ds_stdE","Solution");
    m.result().dataset("ds_stdE").set("solution",s);
    String RIB=String.format(Locale.US,"(abs(x-%.6e[m])<%.6e[m])*(y>%.6e[m])",XR,WB(),HS);
    String[] ex={"freq",pre+"intLN(WPE)",pre+"intLN(WEO)",pre+"("+mbAll("'"+sol+"'")+")",
      "intSolid(solid.rho*(abs(u)^2+abs(v)^2+abs(w)^2))","intLN(abs(u)^2)","intLN(abs(v)^2)","intLN(abs(w)^2)",
      "intLN(solid.Ws)","intAu(solid.Ws)","intLN(solid.Ws*"+RIB+")"};
    double[][][] r=evalGC(m,"ds_stdE",ex);
    double[][] re=r[0], im=r[1];
    int nm=re[0].length;
    List<double[]> cand=new ArrayList<>();
    for(int k=0;k<nm;k++){
      double f=re[0][k], fi=im[0][k], Om=2*Math.PI*f;
      double tr=re[1][k]+re[2][k]+re[3][k], ti=im[1][k]+im[2][k]+im[3][k], ta=Math.hypot(tr,ti);
      double sc=Math.sqrt(2*HBAR/(Om*LA*re[4][k]));
      double[] c=new double[3];
      for(int j=0;j<3;j++) c[j]=ta>0?(re[1+j][k]*tr+im[1+j][k]*ti)/ta*sc:0;
      double dn0=ta*sc;
      double vpl=LAM/(2*dn0)*Math.sqrt(Om*Om*HBAR*RIN/(2*GE*QS));
      double ut=re[5][k]+re[6][k]+re[7][k];
      double q=fi!=0?f/(2*Math.abs(fi)):-1;
      double eL=Math.abs(re[8][k]), eA=Math.abs(re[9][k]);
      System.out.println(String.format(Locale.US,"EIG6I case=%s k=%d f_GHz=%.6f Q=%.1f dn0_MB=%.3f dn0_PE=%.3f dn0_EO=%.3f dn0_tot=%.3f (x1e-12) VpiL_S10_Vcm=%.5f u_frac=%.4f v_frac=%.4f w_frac=%.4f fracAu=%.4f E_rib/E_LN=%.4f",
        CASE,k,f/1e9,q,c[2]*1e12,c[0]*1e12,c[1]*1e12,dn0*1e12,vpl*100,re[5][k]/ut,re[6][k]/ut,re[7][k]/ut,(eL+eA)>0?eA/(eL+eA):-1,eL>0?re[10][k]/re[8][k]:-1));
      if(f>=1.4e9&&f<=3.6e9) cand.add(new double[]{f/1e9,k,dn0});
    }
    cand.sort((a,b)->Double.compare(b[2],a[2]));
    List<double[]> top=new ArrayList<>(cand.subList(0,Math.min(4,cand.size())));
    for(double[] t:top) System.out.println(String.format(Locale.US,"TOP6I case=%s k=%d f_GHz=%.6f dn0_tot=%.3f x1e-12",CASE,(int)t[1],t[0],t[2]*1e12));
    try{ m.sol(s).clearSolutionData(); }catch(Throwable t){}
    return top;
  }

  static String epsXX(){ return fs(NEX*NEX); }
  static String epsYY(){ return fs(NO*NO); }
  static String epsZZ(){ return fs(NO*NO); }
  static String mbH(String s){
    return String.format(Locale.US,"%.10f*abs(withsol(%s,ewfd.Ex))^2+%.10f*abs(withsol(%s,ewfd.Ez))^2+%.10f*abs(withsol(%s,ewfd.Dy)/epsilon0_const)^2",
      NEX*NEX-1,s,NO*NO-1,s,1-1/(NO*NO),s);
  }
  static String mbV(String s){
    return String.format(Locale.US,"%.10f*abs(withsol(%s,ewfd.Ey))^2+%.10f*abs(withsol(%s,ewfd.Ez))^2+%.10f*abs(withsol(%s,ewfd.Dx)/epsilon0_const)^2",
      NO*NO-1,s,NO*NO-1,s,1-1/(NEX*NEX),s);
  }
  /** slanted wall with outward normal (nx,ny); in-plane tangent (ny,-nx); anisotropy projected on n and t only */
  static String mbS(String s,double nx,double ny){
    double tx=ny, ty=-nx, ex=NEX*NEX, ey=NO*NO;
    double ett=ex*tx*tx+ey*ty*ty, enn=ex*nx*nx+ey*ny*ny;
    return String.format(Locale.US,"%.10f*abs(%.10f*withsol(%s,ewfd.Ex)+%.10f*withsol(%s,ewfd.Ey))^2+%.10f*abs(withsol(%s,ewfd.Ez))^2+%.10f*abs((%.10f*withsol(%s,ewfd.Dx)+%.10f*withsol(%s,ewfd.Dy))/epsilon0_const)^2",
      ett-1,tx,s,ty,s,NO*NO-1,s,1-1/enn,nx,s,ny,s);
  }
  static String mbAll(String s){
    double sn=Math.sin(Math.toRadians(ANG)), cs=Math.cos(Math.toRadians(ANG));
    return "intTopB(v*("+mbH(s)+"))+intBotB(-v*("+mbH(s)+"))"
      +"+intWallL(("+fs(-sn)+"*u+"+fs(cs)+"*v)*("+mbS(s,-sn,cs)+"))"
      +"+intWallR(("+fs(sn)+"*u+"+fs(cs)+"*v)*("+mbS(s,sn,cs)+"))"
      +"+intEndL(-u*("+mbV(s)+"))+intEndR(u*("+mbV(s)+"))";
  }

  /** crystal (X,Y,Z) = sim (y,z,x): S1=eYY, S2=eZZ, S3=eXX, S4=2eXZ, S5=2eXY, S6=2eYZ; E1=Ey, E2=0, E3=Ex */
  static void defineVars(Model m,String sol){
    String s="'"+sol+"'";
    double eO=NO*NO, eE=NEX*NEX;
    String[][] v={
      {"Ox","withsol("+s+",ewfd.Ex)"},{"Oy","withsol("+s+",ewfd.Ey)"},{"Oz","withsol("+s+",ewfd.Ez)"},
      {"S1","solid.eYY"},{"S2","solid.eZZ"},{"S3","solid.eXX"},{"S4","2*solid.eXZ"},{"S5","2*solid.eXY"},{"S6","2*solid.eYZ"},
      {"Ec1","es.Ey"},{"Ec2","0"},{"Ec3","es.Ex"},
      {"p11","-0.026"},{"p12","0.090"},{"p13","0.133"},{"p14","-0.075"},{"p31","0.179"},{"p33","0.071"},{"p41","-0.151"},{"p44","0.146"},
      {"r13","8.6e-12[m/V]"},{"r22","3.4e-12[m/V]"},{"r33","30.8e-12[m/V]"},{"r51","28e-12[m/V]"},
      {"dP1","p11*S1+p12*S2+p13*S3+p14*S4"},{"dP2","p12*S1+p11*S2+p13*S3-p14*S4"},{"dP3","p31*(S1+S2)+p33*S3"},
      {"dP4","p41*S1-p41*S2+p44*S4"},{"dP5","p44*S5+p41*S6"},{"dP6","p14*S5+(p11-p12)/2*S6"},
      {"dE1","r13*Ec3-r22*Ec2"},{"dE2","r13*Ec3+r22*Ec2"},{"dE3","r33*Ec3"},{"dE4","r51*Ec2"},{"dE5","r51*Ec1"},{"dE6","-r22*Ec1"},
      {"eX",fs(eO)},{"eY",fs(eO)},{"eZ",fs(eE)}
    };
    m.component("comp1").variable().create("vPert");
    m.component("comp1").variable("vPert").selection().geom("geom1",2);
    m.component("comp1").variable("vPert").selection().named("selLN");
    for(String[] kv:v) m.component("comp1").variable("vPert").set(kv[0],kv[1]);
    for(String t:new String[]{"P","E"}){
      String d=t.equals("P")?"dP":"dE";
      String xx="(-eZ*eZ*"+d+"3)", yy="(-eX*eX*"+d+"1)", zz="(-eY*eY*"+d+"2)", xy="(-eZ*eX*"+d+"5)", xz="(-eZ*eY*"+d+"4)", yz="(-eX*eY*"+d+"6)";
      m.component("comp1").variable("vPert").set("W"+t+(t.equals("P")?"E":"O"),
        xx+"*abs(Ox)^2+"+yy+"*abs(Oy)^2+"+zz+"*abs(Oz)^2+2*("+xy+"*realdot(Ox,Oy)+"+xz+"*realdot(Ox,Oz)+"+yz+"*realdot(Oy,Oz))");
    }
  }
  static String fs(double v){ return String.format(Locale.US,"%.10f",v); }

  static int[][] build(Model m)throws Exception{
    m.param().set("etas","5e-4");
    m.param().set("xc",String.format(Locale.US,"%.10e[m]",XR));
    m.component().create("comp1",true);
    GeomSequence g=m.component("comp1").geom().create("geom1",2);
    g.lengthUnit("m");
    rect(g,"rAir",-XAIR,-HAIR,W+2*XAIR,HS+HR+2*HAIR);
    rect(g,"rLn",0,0,W,HS);
    double wb=WB();
    g.create("pRib","Polygon");
    try{
      g.feature("pRib").set("source","table");
      g.feature("pRib").set("table",new double[][]{{XR-wb,HS},{XR+wb,HS},{XR+WT/2,HS+HR},{XR-WT/2,HS+HR}});
    }catch(Throwable t){
      System.out.println("WARN polygon table: "+t.getMessage()+" -> vectors");
      g.feature("pRib").set("source","vectors");
      g.feature("pRib").set("x",String.format(Locale.US,"%.12e %.12e %.12e %.12e",XR-wb,XR+wb,XR+WT/2,XR-WT/2));
      g.feature("pRib").set("y",String.format(Locale.US,"%.12e %.12e %.12e %.12e",HS,HS,HS+HR,HS+HR));
    }
    for(int i=0;i<4;i++) rect(g,"rAu"+i,XF0+i*PF-WF/2,HS,WF,HAU);
    g.run();
    box(m,"selSlab",2,-1e-9,W+1e-9,-1e-9,HS+1e-9);
    box(m,"selRib",2,XR-wb-1e-9,XR+wb+1e-9,HS-1e-9,HS+HR+1e-9);
    union(m,"selLN",new String[]{"selSlab","selRib"});
    box(m,"selAu",2,XF0-PF,XF0+4*PF,HS-1e-9,HS+HAU+1e-9);
    union(m,"selSolid",new String[]{"selLN","selAu"});
    int[][] G=classify(m,g);
    int nLN=ents(m,"selLN").length, nAu=ents(m,"selAu").length;
    System.out.println(String.format(Locale.US,"GEOM6I nDom=%d nLN=%d(exp 2) nAu=%d(exp 4) nTerm=%d nGnd=%d nTop=%d nBot=%d nWallL=%d nWallR=%d nEndL=%d nEndR=%d nExt=%d",
      g.getNDomains(),nLN,nAu,G[0].length,G[1].length,G[2].length,G[3].length,G[4].length,G[5].length,G[6].length,G[7].length,G[8].length));
    if(nLN!=2||nAu!=4||G[0].length!=2||G[1].length!=2||G[4].length!=1||G[5].length!=1||G[6].length!=1||G[7].length!=1) throw new RuntimeException("selection mismatch");

    Model pz=ModelUtil.load("pz",PZ); Model bs=ModelUtil.load("basic",BASIC);
    Material ln=m.component("comp1").material().create("matLN","Common"); ln.selection().named("selLN");
    copyGroup(ln,pz.material("lithium_niobate"),"def",false); copyGroup(ln,pz.material("lithium_niobate"),"StressCharge",true);
    ModelUtil.remove("basic");
    Model mm=ModelUtil.load("mems",MEMS);
    String auTag=null;
    for(String t:mm.material().tags()){ String lb=mm.material(t).label(); if(t.toLowerCase().contains("gold")||(lb!=null&&(lb.toLowerCase().contains("gold")||lb.startsWith("Au ")))){ auTag=t; break; } }
    if(auTag==null){
      for(String t:mm.material().tags()) System.out.println("MATLIB6I tag="+t+" label="+mm.material(t).label());
      throw new RuntimeException("gold not found in mems lib");
    }
    Material au=m.component("comp1").material().create("matAu","Common"); au.selection().named("selAu");
    copyGroup(au,mm.material(auTag),"def",false);
    String[] grp=mm.material(auTag).propertyGroup().tags();
    System.out.println("MAT6I gold tag="+auTag+" label="+mm.material(auTag).label()+" groups="+Arrays.toString(grp));
    if(Arrays.asList(grp).contains("Enu")) copyGroup(au,mm.material(auTag),"Enu",true);
    ModelUtil.remove("pz"); ModelUtil.remove("mems");
    m.component("comp1").physics().create("solid","SolidMechanics","geom1");
    m.component("comp1").physics("solid").selection().named("selSolid");
    m.component("comp1").physics().create("es","Electrostatics","geom1");
    if(ESAIR){
      box(m,"selBox",2,-XAIR-1e-9,W+XAIR+1e-9,-HAIR-1e-9,HS+HR+HAIR+1e-9);
      m.component("comp1").selection().create("selEs","Difference");
      m.component("comp1").selection("selEs").set("entitydim","2");
      m.component("comp1").selection("selEs").set("add",new String[]{"selBox"});
      m.component("comp1").selection("selEs").set("subtract",new String[]{"selAu"});
      m.component("comp1").physics("es").selection().named("selEs");
      String[] ft=m.component("comp1").physics("es").feature().tags();
      System.out.println("ES6I features="+Arrays.toString(ft));
      if(!Arrays.asList(ft).contains("fsp1")) throw new RuntimeException("no free-space default");
      System.out.println("ESAIR6I es domains="+Arrays.toString(ents(m,"selEs"))+" termX="+G[9].length+" gndX="+G[10].length);
      if(G[9].length!=6||G[10].length!=6) throw new RuntimeException("finger edge mismatch");
    }else m.component("comp1").physics("es").selection().named("selLN");
    m.component("comp1").physics("solid").create("pzm1","PiezoelectricMaterialModel",2); m.component("comp1").physics("solid").feature("pzm1").selection().named("selLN");
    m.component("comp1").multiphysics().create("pze1","PiezoelectricEffect","geom1");
    m.component("comp1").physics("es").create("ccp1","ChargeConservationPiezo",2); m.component("comp1").physics("es").feature("ccp1").selection().named("selLN");
    Object sys=m.component("comp1").coordSystem().create("sys2","Rotated"); sS(sys,"rotationSequence","ZXZ"); sA(sys,"angle",new String[]{"90[deg]","90[deg]","0"});
    sS(m.component("comp1").physics("solid").feature("pzm1"),"coordinateSystem","sys2"); sS(m.component("comp1").physics("es").feature("ccp1"),"coordinateSystem","sys2");
    m.component("comp1").physics("solid").feature("pzm1").create("dmp1","Damping",2);
    m.component("comp1").physics("solid").feature("pzm1").feature("dmp1").set("DampingType","IsotropicLossFactor");
    m.component("comp1").physics("solid").feature("pzm1").feature("dmp1").set("eta_s_mat","userdef");
    m.component("comp1").physics("solid").feature("pzm1").feature("dmp1").set("eta_s","etas");
    m.component("comp1").physics("es").create("term1","Terminal",1); m.component("comp1").physics("es").feature("term1").selection().set(TERM(G));
    m.component("comp1").physics("es").feature("term1").set("TerminalType","Voltage");
    m.component("comp1").physics("es").feature("term1").set("V0","1[V]");
    m.component("comp1").physics("es").create("gnd1","Ground",1); m.component("comp1").physics("es").feature("gnd1").selection().set(cat(G[1],ESAIR?G[10]:new int[0]));
    Object pr=m.component("comp1").physics("solid").prop("Type2D"); sS(pr,"ModeExtension","1"); sS(pr,"kz","0");

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
    sS(w2,"epsilonr_mat","userdef"); sA(w2,"epsilonr",new String[]{epsXX(),"0","0","0",epsYY(),"0","0","0",epsZZ()});
    sS(w2,"mur_mat","userdef"); sA(w2,"mur",new String[]{"1","0","0","0","1","0","0","0","1"});
    sS(w2,"sigma_mat","userdef"); sA(w2,"sigma",new String[]{"0","0","0","0","0","0","0","0","0"});
    m.component("comp1").physics("ewfd").create("weeAu","WaveEquationElectric",2);
    m.component("comp1").physics("ewfd").feature("weeAu").selection().named("selAu");
    Object w3=m.component("comp1").physics("ewfd").feature("weeAu");
    sS(w3,"DisplacementFieldModel","RefractiveIndex");
    sS(w3,"n_mat","userdef"); sA(w3,"n",new String[]{""+N_AU,"0","0","0",""+N_AU,"0","0","0",""+N_AU});
    sS(w3,"ki_mat","userdef"); sA(w3,"ki",new String[]{""+K_AU,"0","0","0",""+K_AU,"0","0","0",""+K_AU});
    m.component("comp1").physics("ewfd").create("sctr1","Scattering",1);
    m.component("comp1").physics("ewfd").feature("sctr1").selection().set(G[8]);

    cpl(m,"intAll",2,null); cpl(m,"intLN",2,"selLN"); cpl(m,"intAu",2,"selAu"); cpl(m,"intSolid",2,"selSolid");
    cplE(m,"intTopB",G[2]); cplE(m,"intBotB",G[3]); cplE(m,"intWallL",G[4]); cplE(m,"intWallR",G[5]); cplE(m,"intEndL",G[6]); cplE(m,"intEndR",G[7]);

    m.component("comp1").mesh().create("mesh1");
    m.component("comp1").mesh("mesh1").feature("size").set("custom","on");
    m.component("comp1").mesh("mesh1").feature("size").set("hmax","150[nm]");
    m.component("comp1").mesh("mesh1").feature("size").set("hmin","1[nm]");
    msize(m,"szLN","selLN","30[nm]");
    msize(m,"szAu","selAu","10[nm]");
    m.component("comp1").mesh("mesh1").create("ftri1","FreeTri");
    m.component("comp1").mesh("mesh1").run();
    System.out.println(String.format(Locale.US,"NUMELEM6I n_elem=%d",m.component("comp1").mesh("mesh1").getNumElem()));
    return G;
  }

  /** G: 0 term (under fingers 0,2), 1 gnd (fingers 1,3), 2 LN top + rib top, 3 LN bottom, 4 wallL, 5 wallR, 6 endL, 7 endR, 8 outer air */
  static int[][] classify(Model m,GeomSequence g){
    double tol=1e-11, wb=WB();
    List<Integer> term=new ArrayList<>(),gnd=new ArrayList<>(),top=new ArrayList<>(),bot=new ArrayList<>(),wl=new ArrayList<>(),wr=new ArrayList<>(),el=new ArrayList<>(),er=new ArrayList<>(),ext=new ArrayList<>(),termX=new ArrayList<>(),gndX=new ArrayList<>();
    int nE=g.getNEdges();
    for(int e=1;e<=nE;e++){
      double[][] q=g.edgeX(e,new double[]{0.0,0.5,1.0});
      double x0=q[0][0],y0=q[0][1],xm=q[1][0],ym=q[1][1],x1=q[2][0],y1=q[2][1];
      boolean hor=Math.abs(y0-y1)<tol, ver=Math.abs(x0-x1)<tol;
      if(ver&&(Math.abs(xm+XAIR)<tol||Math.abs(xm-W-XAIR)<tol)){ ext.add(e); continue; }
      if(hor&&(Math.abs(ym+HAIR)<tol||Math.abs(ym-HS-HR-HAIR)<tol)){ ext.add(e); continue; }
      if(ver&&Math.abs(xm)<tol&&ym>0&&ym<HS){ el.add(e); continue; }
      if(ver&&Math.abs(xm-W)<tol&&ym>0&&ym<HS){ er.add(e); continue; }
      if(hor&&Math.abs(ym)<tol&&xm>0&&xm<W){ bot.add(e); continue; }
      if(hor&&Math.abs(ym-HS)<tol&&xm>0&&xm<W){
        if(Math.abs(xm-XR)<wb) continue;
        boolean done=false;
        for(int i=0;i<4;i++){
          double xc=XF0+i*PF;
          if(Math.abs(xm-xc)<WF/2&&Math.abs(Math.hypot(x1-x0,y1-y0)-WF)<1e-10){ (i%2==0?term:gnd).add(e); done=true; break; }
        }
        if(!done) top.add(e);
        continue;
      }
      if(hor&&Math.abs(ym-HS-HR)<tol&&Math.abs(xm-XR)<WT/2){ top.add(e); continue; }
      if(!hor&&!ver&&ym>HS&&ym<HS+HR){ (xm<XR?wl:wr).add(e); continue; }
      for(int i=0;i<4;i++){
        double xc=XF0+i*PF;
        boolean side=ver&&Math.abs(Math.abs(xm-xc)-WF/2)<tol&&ym>HS&&ym<HS+HAU;
        boolean cap=hor&&Math.abs(ym-HS-HAU)<tol&&Math.abs(xm-xc)<WF/2;
        if(side||cap){ (i%2==0?termX:gndX).add(e); break; }
      }
    }
    int[][] G=new int[11][];
    G[0]=ia(term); G[1]=ia(gnd); G[2]=ia(top); G[3]=ia(bot); G[4]=ia(wl); G[5]=ia(wr); G[6]=ia(el); G[7]=ia(er); G[8]=ia(ext); G[9]=ia(termX); G[10]=ia(gndX);
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
    double[][] v=evalG(m,ds,new String[]{"real(ewfd.neff)","imag(ewfd.neff)","intAll(abs(ewfd.Ex)^2)","intAll(ewfd.normE^2)","intAll(ewfd.normE^2*(abs(x-xc)<0.7[um]))"});
    return new double[]{v[0][k],v[1][k],8.686*K0*Math.abs(v[1][k])/100,v[2][k]/v[3][k],v[4][k]/v[3][k]};
  }
  static double[] pickTE0(Model m,String ds){
    double[][] v=evalG(m,ds,new String[]{"real(ewfd.neff)","imag(ewfd.neff)","intAll(abs(ewfd.Ex)^2)","intAll(ewfd.normE^2)","intAll(ewfd.normE^2*(abs(x-xc)<0.7[um]))"});
    double[] best=null;
    for(int k=0;k<v[0].length;k++){
      double te=v[2][k]/v[3][k], rf=v[4][k]/v[3][k], db=8.686*K0*Math.abs(v[1][k])/100;
      System.out.println(String.format(Locale.US,"MODE6I k=%d neff_re=%.6f neff_im=%.4e dBcm=%.4f TEfrac=%.4f ribFrac=%.4f",k,v[0][k],v[1][k],db,te,rf));
      if(te>0.8&&rf>0.3&&(best==null||v[0][k]>best[0])) best=new double[]{v[0][k],v[1][k],db,te,rf};
    }
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

  static int[] TERM(int[][] G){ return cat(G[0],ESAIR?G[9]:new int[0]); }
  static int[] cat(int[] a,int[] b){ int[] r=Arrays.copyOf(a,a.length+b.length); System.arraycopy(b,0,r,a.length,b.length); return r; }
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
