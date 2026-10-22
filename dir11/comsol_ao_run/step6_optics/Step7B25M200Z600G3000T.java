import com.comsol.model.*;
import com.comsol.model.util.*;
import java.util.*;
import java.util.Locale;

/** Step 7: 3D check of one feed segment of the 6j design (FN7, ridge 400 nm, p = 1.9277 um, free membrane ends in x).
 *  comp1 (2D): TE0 optical mode, exported on a grid and read back as interpolation functions.
 *  comp2 (3D): piezo acoustics of a cell periodic along the waveguide (z), length LZ.
 *    U<Lz>   : fingers continuous along z, no bus bars (must reproduce the 2D FN7 result).
 *    B<Lz>   : one segment per cell: gap ZG/2 | signal bus ZB | tip gap ZT | fingers | tip gap | ground bus ZB | gap ZG/2.
 *    optional M<nm>: in-plane mesh size (default 150 nm); Z<nm>: mesh size along z (default 600 nm);
 *    G<nm>: segment gap ZG; b<nm>: bus width ZB; t<nm>: tip gap ZT;
 *    T: slab etched through in the segment gap except a strip of width WK around the ridge (trench walls get no
 *       moving-boundary term; the optical field there is negligible); W: wide driven sweep instead of eigen + narrow sweep.
 *  Optical fields inside LN use Dx/eps0/ne^2, Dy/eps0/no^2, Ez (all continuous across the LN/air interfaces). */
public class Step7B25M200Z600G3000T {
  static final String PZ="D:\\COMSOL63\\Multiphysics\\data\\comsol_piezo_lib.mph";
  static final String BASIC="D:\\COMSOL63\\Multiphysics\\data\\comsol_basic_material_lib.mph";
  static final String CASE="B25M200Z600G3000T";
  static final String C2="comp2";
  static final int NP=7, ID=3;
  static final int[] DEF={2,3,4};
  static final double P_UM=1.9277, P=P_UM*1e-6, LS=NP*P, XC=(ID+0.5)*P;
  static final double WR=1.0e-6, HLN=400e-9, HAIR=2e-6, HR=400e-9, HAL=100e-9;
  static final double NO=2.211, NEX=2.138, N_AL=1.44, K_AL=16.0, LAM=1.55e-6, K0=2*Math.PI/LAM;
  static final double HBAR=1.054571817e-34, LA=100e-6;
  static double ZB=2e-6, ZT=0.5e-6, ZG=1e-6;
  static final double WK=4e-6;
  static double LZ=2e-6, HXY=150e-9, HZ=600e-9;
  static boolean BUS=false, TR=false;
  static double[] ZP;

  public static void main(String[] args){
    try{
      ModelUtil.initStandalone(true);
      String cs=CASE;
      java.util.regex.Matcher mm=java.util.regex.Pattern.compile("([UB])(\\d+)(?:M(\\d+))?(?:Z(\\d+))?(?:G(\\d+))?(?:b(\\d+))?(?:t(\\d+))?(T)?(W)?").matcher(cs);
      if(!mm.matches()) throw new RuntimeException("unknown case "+cs);
      BUS=mm.group(1).equals("B"); LZ=Double.parseDouble(mm.group(2))*1e-6;
      if(mm.group(3)!=null) HXY=Double.parseDouble(mm.group(3))*1e-9;
      if(mm.group(4)!=null) HZ=Double.parseDouble(mm.group(4))*1e-9;
      if(mm.group(5)!=null) ZG=Double.parseDouble(mm.group(5))*1e-9;
      if(mm.group(6)!=null) ZB=Double.parseDouble(mm.group(6))*1e-9;
      if(mm.group(7)!=null) ZT=Double.parseDouble(mm.group(7))*1e-9;
      TR=mm.group(8)!=null;
      boolean WIDE=mm.group(9)!=null;
      if(TR&&!BUS) throw new RuntimeException("trench needs bus layout");
      ZP=BUS?new double[]{ZG/2,ZG/2+ZB,ZG/2+ZB+ZT,LZ-ZG/2-ZB-ZT,LZ-ZG/2-ZB,LZ-ZG/2,LZ}:new double[]{LZ};
      System.out.println("STEP7_START case="+cs);
      System.out.println(String.format(Locale.US,"CFG7 case=%s bus=%b trench=%b Lz_um=%.3f hxy_nm=%.0f hz_nm=%.0f p_um=%.6f NP=%d hR_nm=%.0f hAl_nm=%.0f ZB_um=%.2f ZT_um=%.2f ZG_um=%.2f overlap_um=%.3f zplanes_um=%s",
        cs,BUS,TR,LZ*1e6,HXY*1e9,HZ*1e9,P_UM,NP,HR*1e9,HAL*1e9,ZB*1e6,ZT*1e6,ZG*1e6,(BUS?ZP[3]-ZP[2]:LZ)*1e6,Arrays.toString(Arrays.stream(ZP).map(z->Math.round(z*1e9)/1e3).toArray())));

      Model m=ModelUtil.create("M7");
      build2D(m);
      Object[] op=optics(m,cs);
      if(op==null){ System.out.println("STEP7_STOP no TE0"); return; }
      double Pw=(Double)op[0];
      String optf="D:\\comsol_ao_run\\s7opt_"+cs+".txt";
      exportOpt(m,(String)op[1],optf);

      build3D(m);
      optFuncs(m,optf);
      defineVars3(m);
      String pre=String.format(Locale.US,"epsilon0_const*c_const/(4*(%.12e))/(%.12e)*",Pw,LZ);

      double[] mode;
      TreeSet<Double> fs=new TreeSet<>();
      if(WIDE){
        mode=new double[]{Double.NaN,Double.NaN,Double.NaN};
        for(int i=0;i<=120;i++) fs.add(Math.round((3.196+0.00025*i)*1e7)/1e7);
      }else{
        mode=eigen3(m,cs,pre);
        if(mode==null){ System.out.println("STEP7_STOP no coupled mode"); return; }
        for(int i=-12;i<=12;i++) fs.add(Math.round((mode[0]+0.000125*i)*1e7)/1e7);
      }
      double[][] d=sweep3(m,"stdF",fs,pre);
      double[] pk=peak(d,cs);
      int ib=-1;
      for(int k=0;k<d.length;k++) if(d[k][1]>=0.5*pk[1]&&(ib<0||d[k][2]/(d[k][1]*d[k][1])<d[ib][2]/(d[ib][1]*d[ib][1]))) ib=k;
      System.out.println(String.format(Locale.US,"BEST7 case=%s f_GHz=%.6f abs_tot=%.4e ReY_Spm=%.4e ImY_Spm=%.4e PL_min_Wm=%.4e",
        cs,d[ib][0],d[ib][1],d[ib][2],d[ib][3],d[ib][2]*Math.pow(LAM/(2*d[ib][1]),2)/2));
      double PL=pk[3]*Math.pow(LAM/(2*pk[1]),2)/2;
      System.out.println(String.format(Locale.US,"RESULT7 case=%s f_eig_GHz=%.6f dn0_eig=%.3f PL_eig_Wm=%.4e f_pk_GHz=%.6f abs_tot=%.4e ReY_Spm=%.4e ImY_Spm=%.4e Q_drv=%.1f PL_drv_Wm=%.4e",
        cs,mode[0],mode[1],mode[2],pk[0],pk[1],pk[3],pk[4],pk[2],PL));
      ModelUtil.remove("M7");
      System.out.println("STEP7_DONE case="+cs);
    }catch(Throwable t){ System.out.println("STEP7_ABORT"); t.printStackTrace(System.out); }
  }

  // ---------------- 2D optics (comp1) ----------------
  static void build2D(Model m)throws Exception{
    m.param().set("p",String.format(Locale.US,"%.10f[um]",P_UM));
    m.param().set("dnL","0");
    m.param().set("etas","5e-4");
    m.component().create("comp1",true);
    GeomSequence g=m.component("comp1").geom().create("geom1",2);
    g.lengthUnit("m");
    rect(g,"airB",0,-HAIR,LS,HAIR);
    rect(g,"airT",0,HLN,LS,HAIR);
    rect(g,"rLn",0,0,LS,HLN);
    rect(g,"rRg",XC-WR/2,HLN,WR,HR);
    for(int c=0;c<NP;c++){
      if(isDef(c)) continue;
      rect(g,"rAp"+c,c*P+0.125*P,HLN,0.25*P,HAL);
      rect(g,"rAn"+c,c*P+0.625*P,HLN,0.25*P,HAL);
    }
    g.run();
    box(m,"selSlab",2,-1e-9,LS+1e-9,-1e-9,HLN+1e-9);
    box(m,"selRidge",2,XC-WR/2-1e-9,XC+WR/2+1e-9,HLN-1e-9,HLN+HR+1e-9);
    union(m,"selLN",new String[]{"selSlab","selRidge"});
    box(m,"selAlL",2,-1e-9,XC-WR/2-1e-9,HLN-1e-9,HLN+HAL+1e-9);
    box(m,"selAlR",2,XC+WR/2+1e-9,LS+1e-9,HLN-1e-9,HLN+HAL+1e-9);
    union(m,"selAl",new String[]{"selAlL","selAlR"});
    List<Integer> ext=new ArrayList<>();
    for(int e=1;e<=g.getNEdges();e++){
      double[][] q=g.edgeX(e,new double[]{0.0,0.5,1.0});
      double xm=q[1][0], ym=q[1][1];
      boolean ver=Math.abs(q[0][0]-q[2][0])<1e-11, hor=Math.abs(q[0][1]-q[2][1])<1e-11;
      if(ver&&(Math.abs(xm)<1e-11||Math.abs(xm-LS)<1e-11)) ext.add(e);
      else if(hor&&(Math.abs(ym+HAIR)<1e-11||Math.abs(ym-HLN-HAIR)<1e-11)) ext.add(e);
    }
    System.out.println("GEOM7_2D nLN="+ents(m,"selLN").length+" nAl="+ents(m,"selAl").length+" nExt="+ext.size());

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
    sS(w2,"epsilonr_mat","userdef"); sA(w2,"epsilonr",new String[]{e2,"0","0","0",o2,"0","0","0",o2});
    sS(w2,"mur_mat","userdef"); sA(w2,"mur",new String[]{"1","0","0","0","1","0","0","0","1"});
    sS(w2,"sigma_mat","userdef"); sA(w2,"sigma",new String[]{"0","0","0","0","0","0","0","0","0"});
    m.component("comp1").physics("ewfd").create("weeAl","WaveEquationElectric",2);
    m.component("comp1").physics("ewfd").feature("weeAl").selection().named("selAl");
    Object w3=m.component("comp1").physics("ewfd").feature("weeAl");
    sS(w3,"DisplacementFieldModel","RefractiveIndex");
    sS(w3,"n_mat","userdef"); sA(w3,"n",new String[]{""+N_AL,"0","0","0",""+N_AL,"0","0","0",""+N_AL});
    sS(w3,"ki_mat","userdef"); sA(w3,"ki",new String[]{""+K_AL,"0","0","0",""+K_AL,"0","0","0",""+K_AL});
    m.component("comp1").physics("ewfd").create("sctr1","Scattering",1);
    m.component("comp1").physics("ewfd").feature("sctr1").selection().set(ia(ext));
    cpl(m,"intAll",2,null);
    m.param().set("xc",String.format(Locale.US,"%.10e[m]",XC));
    m.component("comp1").mesh().create("mesh1");
    m.component("comp1").mesh("mesh1").feature("size").set("custom","on");
    m.component("comp1").mesh("mesh1").feature("size").set("hmax","150[nm]");
    m.component("comp1").mesh("mesh1").feature("size").set("hmin","1[nm]");
    msize(m,"szLN","selLN","30[nm]");
    msize(m,"szAl","selAl","10[nm]");
    m.component("comp1").mesh("mesh1").create("ftri1","FreeTri");
    m.component("comp1").mesh("mesh1").run();
  }

  static Object[] optics(Model m,String lab){
    String[] o1=optStudy(m,"stdO1",20,"1.920");
    double[] te=pickTE0(m,o1[1],lab);
    if(te==null) return null;
    String[] o2=optStudy(m,"stdO2",1,String.format(Locale.US,"%.6f",te[0]));
    double[] t2=modeRow(m,o2[1],0);
    double Pw=evalG(m,o2[1],new String[]{"intAll(ewfd.Poavz)"})[0][0];
    System.out.println(String.format(Locale.US,"SOLOPT7 case=%s neff=%.8f dBcm=%.4f TEfrac=%.4f ridgeFrac=%.4f P=%.8e W/m",lab,t2[0],t2[2],t2[3],t2[4],Pw));
    if(Math.abs(t2[0]-te[0])>1e-6||t2[3]<0.8) return null;
    return new Object[]{Pw,o2[1]};
  }

  static void exportOpt(Model m,String ds,String f){
    String[] q={"ewfd.Dx/epsilon0_const","ewfd.Dy/epsilon0_const","ewfd.Ex","ewfd.Ey","ewfd.Ez"};
    String[] ex=new String[10];
    for(int i=0;i<5;i++){ ex[2*i]="real("+q[i]+")"; ex[2*i+1]="imag("+q[i]+")"; }
    m.result().export().create("eopt","Data");
    m.result().export("eopt").set("data",ds);
    m.result().export("eopt").set("expr",ex);
    m.result().export("eopt").set("location","grid");
    m.result().export("eopt").set("gridx2",String.format(Locale.US,"range(0,1e-8,%.10e)",LS));
    m.result().export("eopt").set("gridy2",String.format(Locale.US,"range(-2e-8,1e-8,%.10e)",HLN+HR+2e-8));
    m.result().export("eopt").set("header","off");
    m.result().export("eopt").set("filename",f);
    m.result().export("eopt").run();
    System.out.println("OPTEXPORT7 file="+f);
  }

  static void optFuncs(Model m,String f){
    String[] n={"oDxr","oDxi","oDyr","oDyi","oExr","oExi","oEyr","oEyi","oEzr","oEzi"};
    String[][] fu=new String[10][];
    for(int i=0;i<10;i++) fu[i]=new String[]{n[i],""+(i+1)};
    m.func().create("fopt","Interpolation");
    m.func("fopt").set("source","file");
    m.func("fopt").set("filename",f);
    m.func("fopt").set("struct","spreadsheet");
    m.func("fopt").set("nargs","2");
    m.func("fopt").set("funcs",fu);
    m.func("fopt").set("interp","linear");
    m.func("fopt").set("extrap","const");
    m.func("fopt").importData();
    System.out.println("OPTFUNC7 ok");
  }

  // ---------------- 3D acoustics (comp2) ----------------
  static List<double[]> pieces(){
    List<double[]> r=new ArrayList<>();
    int[][] grp={{0,DEF[0]-1},{DEF[DEF.length-1]+1,NP-1}};
    for(int[] gr:grp){
      for(int c=gr[0];c<=gr[1];c++){
        r.add(new double[]{c*P+0.125*P,c*P+0.375*P,1});
        r.add(new double[]{c*P+0.375*P,c*P+0.625*P,0});
        r.add(new double[]{c*P+0.625*P,c*P+0.875*P,2});
        if(c<gr[1]) r.add(new double[]{c*P+0.875*P,(c+1)*P+0.125*P,0});
      }
    }
    return r;
  }

  static void build3D(Model m)throws Exception{
    m.component().create(C2,true);
    GeomSequence g=m.component(C2).geom().create("geom2",3);
    g.lengthUnit("m");
    g.create("wp1","WorkPlane");
    g.feature("wp1").set("quickplane","xy");
    g.feature("wp1").set("unite",true);
    GeomSequence w=g.feature("wp1").geom();
    rect(w,"rLn",0,0,LS,HLN);
    rect(w,"rRg",XC-WR/2,HLN,WR,HR);
    if(TR) rect(w,"rLnC",XC-WK/2,0,WK,HLN);
    List<double[]> pc=pieces();
    for(int i=0;i<pc.size();i++) rect(w,"rA"+i,pc.get(i)[0],HLN,pc.get(i)[1]-pc.get(i)[0],HAL);
    g.create("ext1","Extrude");
    g.feature("ext1").set("workplane","wp1");
    g.feature("ext1").selection("input").set(new String[]{"wp1"});
    String[] dist=new String[ZP.length]; String[][] sc=new String[ZP.length][], dp=new String[ZP.length][]; String[] tw=new String[ZP.length];
    for(int i=0;i<ZP.length;i++){ dist[i]=String.format(Locale.US,"%.12e",ZP[i]); sc[i]=new String[]{"1","1"}; dp[i]=new String[]{"0","0"}; tw[i]="0"; }
    g.feature("ext1").set("distance",dist);
    g.feature("ext1").set("scale",sc);
    g.feature("ext1").set("displ",dp);
    g.feature("ext1").set("twist",tw);
    g.run();
    System.out.println("GEOM7_3D nDom="+g.getNDomains()+" nBnd="+g.getNBoundaries());

    double t=1e-9, yA=HLN-t, yB=HLN+HAL+t;
    box3(m,"s3Slab",3,-t,LS+t,-t,HLN+t,-t,LZ+t);
    box3(m,"s3Rg",3,XC-WR/2-t,XC+WR/2+t,HLN-t,HLN+HR+t,-t,LZ+t);
    if(TR){
      box3(m,"s3Tr1",3,-t,XC-WK/2+t,-t,HLN+t,-t,ZP[0]+t);
      box3(m,"s3Tr2",3,XC+WK/2-t,LS+t,-t,HLN+t,-t,ZP[0]+t);
      box3(m,"s3Tr3",3,-t,XC-WK/2+t,-t,HLN+t,ZP[5]-t,LZ+t);
      box3(m,"s3Tr4",3,XC+WK/2-t,LS+t,-t,HLN+t,ZP[5]-t,LZ+t);
      uni3(m,"s3Tr",3,new String[]{"s3Tr1","s3Tr2","s3Tr3","s3Tr4"});
      m.component(C2).selection().create("s3SlabK","Difference");
      m.component(C2).selection("s3SlabK").set("entitydim","3");
      m.component(C2).selection("s3SlabK").set("add",new String[]{"s3Slab"});
      m.component(C2).selection("s3SlabK").set("subtract",new String[]{"s3Tr"});
      uni3(m,"selLN3",3,new String[]{"s3SlabK","s3Rg"});
      System.out.println("TRENCH7 nTr="+e3(m,"s3Tr")+" nSlabKept="+e3(m,"s3SlabK"));
    }else uni3(m,"selLN3",3,new String[]{"s3Slab","s3Rg"});
    List<String> sg=new ArrayList<>(), gd=new ArrayList<>();
    double[][] span={{0.125*P,(DEF[0]-1)*P+0.875*P},{(DEF[DEF.length-1]+1)*P+0.125*P,(NP-1)*P+0.875*P}};
    int k=0;
    if(BUS){
      for(double[] s:span){ box3(m,"s3SB"+k,3,s[0]-t,s[1]+t,yA,yB,ZP[0]-t,ZP[1]+t); sg.add("s3SB"+k);
                            box3(m,"s3GB"+k,3,s[0]-t,s[1]+t,yA,yB,ZP[4]-t,ZP[5]+t); gd.add("s3GB"+k); k++; }
    }
    for(int i=0;i<pc.size();i++){
      double[] q=pc.get(i);
      if(q[2]==1){ box3(m,"s3S"+i,3,q[0]-t,q[1]+t,yA,yB,(BUS?ZP[1]:0)-t,(BUS?ZP[3]:LZ)+t); sg.add("s3S"+i); }
      if(q[2]==2){ box3(m,"s3G"+i,3,q[0]-t,q[1]+t,yA,yB,(BUS?ZP[2]:0)-t,(BUS?ZP[4]:LZ)+t); gd.add("s3G"+i); }
    }
    uni3(m,"selSig3",3,sg.toArray(new String[0]));
    uni3(m,"selGnd3",3,gd.toArray(new String[0]));
    uni3(m,"selAl3",3,new String[]{"selSig3","selGnd3"});
    uni3(m,"selSolid3",3,new String[]{"selLN3","selAl3"});
    adj3(m,"a3Sig","selSig3"); adj3(m,"a3Gnd","selGnd3"); adj3(m,"a3LN","selLN3");
    int3(m,"selTerm3",new String[]{"a3Sig","a3LN"});
    int3(m,"selGndF3",new String[]{"a3Gnd","a3LN"});
    box3(m,"b3Z0",2,-t,LS+t,-t,HLN+HR+t,-t,t);
    box3(m,"b3ZL",2,-t,LS+t,-t,HLN+HR+t,LZ-t,LZ+t);
    box3(m,"b3TopAll",2,-t,LS+t,HLN-t,HLN+t,-t,LZ+t);
    box3(m,"b3UnderRg",2,XC-WR/2-t,XC+WR/2+t,HLN-t,HLN+t,-t,LZ+t);
    box3(m,"b3RgTop",2,XC-WR/2-t,XC+WR/2+t,HLN+HR-t,HLN+HR+t,-t,LZ+t);
    dif3(m,"b3TopLN",new String[]{"b3TopAll"},new String[]{"b3UnderRg","selTerm3","selGndF3"});
    uni3(m,"b3TopU",2,new String[]{"b3TopLN","b3RgTop"});
    int3(m,"b3Top",new String[]{"b3TopU","a3LN"});
    box3(m,"b3BotAll",2,-t,LS+t,-t,t,-t,LZ+t);
    int3(m,"b3Bot",new String[]{"b3BotAll","a3LN"});
    box3(m,"b3WL",2,XC-WR/2-t,XC-WR/2+t,HLN-t,HLN+HR+t,-t,LZ+t);
    box3(m,"b3WR",2,XC+WR/2-t,XC+WR/2+t,HLN-t,HLN+HR+t,-t,LZ+t);
    System.out.println(String.format(Locale.US,"SEL7 nLN=%d nSig=%d nGnd=%d nTerm=%d nGndF=%d nZ0=%d nZL=%d nTop=%d nBot=%d nWL=%d nWR=%d",
      e3(m,"selLN3"),e3(m,"selSig3"),e3(m,"selGnd3"),e3(m,"selTerm3"),e3(m,"selGndF3"),e3(m,"b3Z0"),e3(m,"b3ZL"),e3(m,"b3Top"),e3(m,"b3Bot"),e3(m,"b3WL"),e3(m,"b3WR")));
    if(e3(m,"selTerm3")==0||e3(m,"selGndF3")==0||e3(m,"b3Z0")!=e3(m,"b3ZL")) throw new RuntimeException("selection mismatch 3D");

    Model pz=ModelUtil.load("pz",PZ); Model bs=ModelUtil.load("basic",BASIC);
    Material ln=m.component(C2).material().create("matLN3","Common"); ln.selection().named("selLN3");
    copyGroup(ln,pz.material("lithium_niobate"),"def",false); copyGroup(ln,pz.material("lithium_niobate"),"StressCharge",true);
    Material al=m.component(C2).material().create("matAl3","Common"); al.selection().named("selAl3");
    copyGroup(al,bs.material("aluminum"),"def",false); copyGroup(al,bs.material("aluminum"),"Enu",true);
    ModelUtil.remove("pz"); ModelUtil.remove("basic");
    m.component(C2).physics().create("solid","SolidMechanics","geom2");
    m.component(C2).physics("solid").selection().named("selSolid3");
    m.component(C2).physics().create("es","Electrostatics","geom2");
    m.component(C2).physics("es").selection().named("selLN3");
    m.component(C2).physics("solid").create("pzm1","PiezoelectricMaterialModel",3); m.component(C2).physics("solid").feature("pzm1").selection().named("selLN3");
    m.component(C2).multiphysics().create("pze1","PiezoelectricEffect","geom2");
    m.component(C2).physics("es").create("ccp1","ChargeConservationPiezo",3); m.component(C2).physics("es").feature("ccp1").selection().named("selLN3");
    Object sys=m.component(C2).coordSystem().create("sysR","Rotated");
    sS(sys,"rotationSequence","ZXZ"); sA(sys,"angle",new String[]{"90[deg]","90[deg]","0"});
    System.out.println("SYSR angle="+Arrays.toString(m.component(C2).coordSystem("sysR").getStringArray("angle")));
    sS(m.component(C2).physics("solid").feature("pzm1"),"coordinateSystem","sysR"); sS(m.component(C2).physics("es").feature("ccp1"),"coordinateSystem","sysR");
    m.component(C2).physics("solid").feature("pzm1").create("dmp1","Damping",3);
    m.component(C2).physics("solid").feature("pzm1").feature("dmp1").set("DampingType","IsotropicLossFactor");
    m.component(C2).physics("solid").feature("pzm1").feature("dmp1").set("eta_s_mat","userdef");
    m.component(C2).physics("solid").feature("pzm1").feature("dmp1").set("eta_s","etas");
    m.component(C2).physics("es").create("term1","Terminal",2); m.component(C2).physics("es").feature("term1").selection().named("selTerm3");
    m.component(C2).physics("es").feature("term1").set("TerminalType","Voltage");
    m.component(C2).physics("es").feature("term1").set("V0","1[V]");
    m.component(C2).physics("es").create("gnd1","Ground",2); m.component(C2).physics("es").feature("gnd1").selection().named("selGndF3");
    m.component(C2).physics("es").create("gndT","Ground",2); m.component(C2).physics("es").feature("gndT").selection().named("selTerm3");
    m.component(C2).physics("es").feature("gndT").active(false);
    uni3(m,"b3Per",2,new String[]{"b3Z0","b3ZL"});
    for(String ph:new String[]{"solid","es"}){
      m.component(C2).physics(ph).create("pc1","PeriodicCondition",2);
      m.component(C2).physics(ph).feature("pc1").selection().named("b3Per");
    }

    cpl3(m,"i3LN",3,"selLN3"); cpl3(m,"i3Al",3,"selAl3");
    cpl3(m,"i3Top",2,"b3Top"); cpl3(m,"i3Bot",2,"b3Bot"); cpl3(m,"i3WL",2,"b3WL"); cpl3(m,"i3WR",2,"b3WR");

    m.component(C2).mesh().create("mesh2","geom2");
    m.component(C2).mesh("mesh2").feature("size").set("custom","on");
    m.component(C2).mesh("mesh2").feature("size").set("hmax",String.format(Locale.US,"%.0f[nm]",HZ*1e9));
    m.component(C2).mesh("mesh2").feature("size").set("hmin","5[nm]");
    m.component(C2).mesh("mesh2").create("ftri1","FreeTri");
    m.component(C2).mesh("mesh2").feature("ftri1").selection().named("b3Z0");
    m.component(C2).mesh("mesh2").feature("ftri1").create("sz1","Size");
    m.component(C2).mesh("mesh2").feature("ftri1").feature("sz1").set("custom","on");
    m.component(C2).mesh("mesh2").feature("ftri1").feature("sz1").set("hmaxactive",true);
    m.component(C2).mesh("mesh2").feature("ftri1").feature("sz1").set("hmax",String.format(Locale.US,"%.0f[nm]",HXY*1e9));
    m.component(C2).mesh("mesh2").create("swe1","Sweep");
    m.component(C2).mesh("mesh2").run();
    System.out.println(String.format(Locale.US,"MESH7 n_elem=%d",m.component(C2).mesh("mesh2").getNumElem()));
  }

  static void defineVars3(Model m){
    double eO=NO*NO, eE=NEX*NEX;
    String[][] v={
      {"Ox","(oDxr(x,y)+i*oDxi(x,y))/"+fs(eE)},{"Oy","(oDyr(x,y)+i*oDyi(x,y))/"+fs(eO)},{"Oz","oEzr(x,y)+i*oEzi(x,y)"},
      {"S1","solid.eYY"},{"S2","solid.eZZ"},{"S3","solid.eXX"},{"S4","2*solid.eXZ"},{"S5","2*solid.eXY"},{"S6","2*solid.eYZ"},
      {"Ec1","es.Ey"},{"Ec2","es.Ez"},{"Ec3","es.Ex"},
      {"p11","-0.026"},{"p12","0.090"},{"p13","0.133"},{"p14","-0.075"},{"p31","0.179"},{"p33","0.071"},{"p41","-0.151"},{"p44","0.146"},
      {"r13","8.6e-12[m/V]"},{"r22","3.4e-12[m/V]"},{"r33","30.8e-12[m/V]"},{"r51","28e-12[m/V]"},
      {"dP1","p11*S1+p12*S2+p13*S3+p14*S4"},{"dP2","p12*S1+p11*S2+p13*S3-p14*S4"},{"dP3","p31*(S1+S2)+p33*S3"},
      {"dP4","p41*S1-p41*S2+p44*S4"},{"dP5","p44*S5+p41*S6"},{"dP6","p14*S5+(p11-p12)/2*S6"},
      {"dE1","r13*Ec3-r22*Ec2"},{"dE2","r13*Ec3+r22*Ec2"},{"dE3","r33*Ec3"},{"dE4","r51*Ec2"},{"dE5","r51*Ec1"},{"dE6","-r22*Ec1"},
      {"eX",fs(eO)},{"eY",fs(eO)},{"eZ",fs(eE)}
    };
    m.component(C2).variable().create("vPert3");
    m.component(C2).variable("vPert3").selection().geom("geom2",3);
    m.component(C2).variable("vPert3").selection().named("selLN3");
    for(String[] kv:v) m.component(C2).variable("vPert3").set(kv[0],kv[1]);
    for(String t:new String[]{"P","E"}){
      String d=t.equals("P")?"dP":"dE";
      String xx="(-eZ*eZ*"+d+"3)", yy="(-eX*eX*"+d+"1)", zz="(-eY*eY*"+d+"2)", xy="(-eZ*eX*"+d+"5)", xz="(-eZ*eY*"+d+"4)", yz="(-eX*eY*"+d+"6)";
      m.component(C2).variable("vPert3").set("W"+t+(t.equals("P")?"E":"O"),
        xx+"*abs(Ox)^2+"+yy+"*abs(Oy)^2+"+zz+"*abs(Oz)^2+2*("+xy+"*realdot(Ox,Oy)+"+xz+"*realdot(Ox,Oz)+"+yz+"*realdot(Oy,Oz))");
    }
  }
  static String mbH(){
    return String.format(Locale.US,"(%.10f*((oExr(x,y))^2+(oExi(x,y))^2)+%.10f*((oEzr(x,y))^2+(oEzi(x,y))^2)+%.10f*((oDyr(x,y))^2+(oDyi(x,y))^2))",
      NEX*NEX-1,NO*NO-1,1-1/(NO*NO));
  }
  static String mbV(){
    return String.format(Locale.US,"(%.10f*((oEyr(x,y))^2+(oEyi(x,y))^2)+%.10f*((oEzr(x,y))^2+(oEzi(x,y))^2)+%.10f*((oDxr(x,y))^2+(oDxi(x,y))^2))",
      NO*NO-1,NO*NO-1,1-1/(NEX*NEX));
  }
  static String mbAll(){ return "comp2.i3Top(v*"+mbH()+")+comp2.i3Bot(-v*"+mbH()+")+comp2.i3WL(-u*"+mbV()+")+comp2.i3WR(u*"+mbV()+")"; }

  static String newStudy(Model m,String st,String type,String tag){
    Set<String> sb=new HashSet<>(Arrays.asList(m.sol().tags()));
    m.study().create(st);
    m.study(st).create(tag,type);
    return String.join(",",sb);
  }
  static String runStudy(Model m,String st,String tag,Set<String> sb){
    try{ m.study(st).feature(tag).setEntry("activate","ewfd",false); }catch(Throwable t){ System.out.println("WARN deactivate ewfd: "+t.getMessage()); }
    m.study(st).createAutoSequences("all");
    String s=null; for(String t:m.sol().tags()) if(!sb.contains(t)){ s=t; break; }
    long t0=System.currentTimeMillis();
    m.study(st).run();
    System.out.println(String.format(Locale.US,"STUDY7 %s sol=%s time_s=%.0f",st,s,(System.currentTimeMillis()-t0)/1e3));
    m.result().dataset().create("ds_"+st,"Solution");
    m.result().dataset("ds_"+st).set("solution",s);
    return s;
  }

  /** returns {f_GHz, dn0, PL_eig} of the strongest-coupled mode in 3.0..3.5 GHz */
  static double[] eigen3(Model m,String cs,String pre){
    m.component(C2).physics("es").feature("term1").active(false);
    m.component(C2).physics("es").feature("gndT").active(true);
    Set<String> sb=new HashSet<>(Arrays.asList(m.sol().tags()));
    m.study().create("stdE"); m.study("stdE").create("eig","Eigenfrequency");
    m.study("stdE").feature("eig").set("neigs",BUS?"30":"12");
    m.study("stdE").feature("eig").set("shift","3.21[GHz]");
    m.study("stdE").feature("eig").set("shiftactive","on");
    runStudy(m,"stdE","eig",sb);
    String zc=BUS?String.format(Locale.US,"((z>=%.10e)*(z<=%.10e))",ZP[1],ZP[4]):"1";
    String[] ex={"freq","comp2.i3LN(solid.Ws)","comp2.i3Al(solid.Ws)","comp2.i3LN(abs(u)^2)","comp2.i3LN(abs(v)^2)","comp2.i3LN(abs(w)^2)","comp2.i3LN(solid.Ws*"+zc+")",
      pre+"comp2.i3LN(WPE)",pre+"comp2.i3LN(WEO)",pre+"("+mbAll()+")",
      "comp2.i3LN(solid.rho*(abs(u)^2+abs(v)^2+abs(w)^2))+comp2.i3Al(solid.rho*(abs(u)^2+abs(v)^2+abs(w)^2))"};
    double[][][] r=evalGC(m,"ds_stdE",ex);
    double[][] re=r[0], im=r[1];
    double[] best=null;
    for(int k=0;k<re[0].length;k++){
      double f=re[0][k], fi=im[0][k], Om=2*Math.PI*f, Q=fi!=0?f/(2*Math.abs(fi)):-1;
      double ut=re[3][k]+re[4][k]+re[5][k];
      double tr=re[7][k]+re[8][k]+re[9][k], ti=im[7][k]+im[8][k]+im[9][k], ta=Math.hypot(tr,ti);
      double s0=Math.sqrt(2*HBAR/(Om*LA*re[10][k]/LZ));
      double[] c=new double[3];
      for(int j=0;j<3;j++) c[j]=ta>0?(re[7+j][k]*tr+im[7+j][k]*ti)/ta*s0:0;
      double dn0=ta*s0;
      double PL=dn0>0?HBAR*Om*Om*LAM*LAM/(4*Q*LA*dn0*dn0):-1;
      System.out.println(String.format(Locale.US,"EIG7 case=%s k=%d f_GHz=%.6f Q=%.1f u_frac=%.4f v_frac=%.4f w_frac=%.4f fracAl=%.4f E_core/E_LN=%.4f dn0_MB=%.3f dn0_PE=%.3f dn0_EO=%.3f dn0_tot=%.3f PL_eig_Wm=%.4e",
        cs,k,f/1e9,Q,re[3][k]/ut,re[4][k]/ut,re[5][k]/ut,re[2][k]/(re[1][k]+re[2][k]),re[6][k]/re[1][k],c[2]*1e12,c[0]*1e12,c[1]*1e12,dn0*1e12,PL));
      if(f>3.0e9&&f<3.5e9&&(best==null||dn0*1e12>best[1])) best=new double[]{f/1e9,dn0*1e12,PL};
    }
    m.component(C2).physics("es").feature("gndT").active(false);
    m.component(C2).physics("es").feature("term1").active(true);
    return best;
  }

  /** rows: f, |tot|, ReY/Lz, ImY/Lz */
  static double[][] sweep3(Model m,String st,TreeSet<Double> fs,String pre){
    StringBuilder pl=new StringBuilder();
    for(Double f:fs){ if(pl.length()>0) pl.append(", "); pl.append(String.format(Locale.US,"%.7f[GHz]",f)); }
    Set<String> sb=new HashSet<>(Arrays.asList(m.sol().tags()));
    m.study().create(st); m.study(st).create("freq","Frequency");
    m.study(st).feature("freq").set("plist",pl.toString());
    runStudy(m,st,"freq",sb);
    String[] ex={"freq",pre+"comp2.i3LN(WPE)",pre+"comp2.i3LN(WEO)",pre+"("+mbAll()+")","comp2.es.Q0_1"};
    double[][][] r=evalGC(m,"ds_"+st,ex);
    double[][] re=r[0], im=r[1];
    double[][] d=new double[re[0].length][];
    for(int k=0;k<d.length;k++){
      double f=re[0][k], w=2*Math.PI*f;
      double tr=re[1][k]+re[2][k]+re[3][k], ti=im[1][k]+im[2][k]+im[3][k];
      d[k]=new double[]{f/1e9,Math.hypot(tr,ti),-w*im[4][k]/LZ,w*re[4][k]/LZ};
      System.out.println(String.format(Locale.US,"F7 f_GHz=%.6f PE=(%.4e,%.4e) EO=(%.4e,%.4e) MB=(%.4e,%.4e) abs_tot=%.6e ReY_Spm=%.6e ImY_Spm=%.6e",
        d[k][0],re[1][k],im[1][k],re[2][k],im[2][k],re[3][k],im[3][k],d[k][1],d[k][2],d[k][3]));
    }
    return d;
  }

  /** returns {f, |tot|, Q, ReY, ImY} */
  static double[] peak(double[][] d,String lab){
    Arrays.sort(d,(x,y)->Double.compare(x[0],y[0]));
    int n=d.length, ip=0;
    for(int k=0;k<n;k++) if(d[k][1]>d[ip][1]) ip=k;
    double h=d[ip][1]/Math.sqrt(2), lo=Double.NaN, hi=Double.NaN;
    for(int j=ip;j>0;j--) if(d[j-1][1]<h){ lo=d[j-1][0]+(h-d[j-1][1])*(d[j][0]-d[j-1][0])/(d[j][1]-d[j-1][1]); break; }
    for(int j=ip;j<n-1;j++) if(d[j+1][1]<h){ hi=d[j][0]+(h-d[j][1])*(d[j+1][0]-d[j][0])/(d[j+1][1]-d[j][1]); break; }
    double Q=d[ip][0]/(hi-lo);
    System.out.println(String.format(Locale.US,"PEAK7 set=%s f_peak_GHz=%.6f abs_tot_peak=%.6e FWHM_MHz=%.4f Q=%.1f ReY_Spm=%.6e ImY_Spm=%.6e at_edge=%b",
      lab,d[ip][0],d[ip][1],(hi-lo)*1e3,Q,d[ip][2],d[ip][3],ip==0||ip==n-1));
    return new double[]{d[ip][0],d[ip][1],Q,d[ip][2],d[ip][3]};
  }

  // ---------------- helpers ----------------
  static String[] optStudy(Model m,String st,int neigs,String shift){
    Set<String> sb=new HashSet<>(Arrays.asList(m.sol().tags()));
    m.study().create(st);
    m.study(st).create("mode","ModeAnalysis");
    m.study(st).feature("mode").set("modeFreq","c_const/1.55[um]");
    m.study(st).feature("mode").set("neigsactive",true);
    m.study(st).feature("mode").set("neigs",neigs);
    m.study(st).feature("mode").set("shiftactive",true);
    m.study(st).feature("mode").set("shift",shift);
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
      double te=v[2][k]/v[3][k], rf=v[4][k]/v[3][k];
      if(te>0.8&&(best==null||rf>best[4])) best=new double[]{v[0][k],v[1][k],0,te,rf};
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
  static int e3(Model m,String s){ return m.component(C2).selection(s).entities().length; }
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
  static void box3(Model m,String t,int dim,double xa,double xb,double ya,double yb,double za,double zb){
    m.component(C2).selection().create(t,"Box");
    m.component(C2).selection(t).set("entitydim",""+dim);
    m.component(C2).selection(t).set("condition","inside");
    String[][] kv={{"xmin",""+xa},{"xmax",""+xb},{"ymin",""+ya},{"ymax",""+yb},{"zmin",""+za},{"zmax",""+zb}};
    for(String[] q:kv) m.component(C2).selection(t).set(q[0],String.format(Locale.US,"%.12e",Double.parseDouble(q[1])));
  }
  static void uni3(Model m,String t,int dim,String[] in){
    m.component(C2).selection().create(t,"Union");
    m.component(C2).selection(t).set("entitydim",""+dim);
    m.component(C2).selection(t).set("input",in);
  }
  static void adj3(Model m,String t,String in){
    m.component(C2).selection().create(t,"Adjacent");
    m.component(C2).selection(t).set("input",new String[]{in});
    m.component(C2).selection(t).set("outputdim","2");
  }
  static void int3(Model m,String t,String[] in){
    m.component(C2).selection().create(t,"Intersection");
    m.component(C2).selection(t).set("entitydim","2");
    m.component(C2).selection(t).set("input",in);
  }
  static void dif3(Model m,String t,String[] add,String[] sub){
    m.component(C2).selection().create(t,"Difference");
    m.component(C2).selection(t).set("entitydim","2");
    m.component(C2).selection(t).set("add",add);
    m.component(C2).selection(t).set("subtract",sub);
  }
  static void cpl(Model m,String t,int dim,String sel){
    m.component("comp1").cpl().create(t,"Integration");
    m.component("comp1").cpl(t).selection().geom("geom1",dim);
    if(sel==null) m.component("comp1").cpl(t).selection().all(); else m.component("comp1").cpl(t).selection().named(sel);
  }
  static void cpl3(Model m,String t,int dim,String sel){
    m.component(C2).cpl().create(t,"Integration");
    m.component(C2).cpl(t).selection().geom("geom2",dim);
    m.component(C2).cpl(t).selection().named(sel);
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
  static String fs(double v){ return String.format(Locale.US,"%.10f",v); }
  static void sS(Object o,String n,String v)throws Exception{ o.getClass().getMethod("set",String.class,String.class).invoke(o,n,v); }
  static void sA(Object o,String n,String[] v)throws Exception{ o.getClass().getMethod("set",String.class,String[].class).invoke(o,n,v); }
}
