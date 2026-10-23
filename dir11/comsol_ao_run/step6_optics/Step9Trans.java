import com.comsol.model.*;
import com.comsol.model.util.*;
import java.util.*;

/** Step 9: optical transition between the suspended ridge (air below the film) and the ordinary ridge on SiO2/Si (2D mode analysis, TE0 at 1550 nm).
 *  Cross-section as in Step7 comp1 / Step8Bridge: period 1.84 um, NP = 7 (slab width 12.88 um), ridge 1 um x 400 nm on a 400 nm LN slab,
 *  Al fingers 100 nm (n = 1.44 + 16i) outside the three removed cells (only in the "F" cases).
 *  Cases: S0 suspended, no fingers; SF suspended with fingers; O<box> ridge on SiO2 (box um) over Si, no fingers.
 *  For each case the TE0 fields Ex, Ey, Hx, Hy are exported on a grid (window +-3.5 um around the ridge) for the overlap in post_step9_trans.py.
 *  Usage: Step9Trans [m|f]   m = default mesh, f = finer mesh (convergence check). */
public class Step9Trans {
  static final int NP=7, ID=3; static final int[] DEF={2,3,4};
  static final double P=1.84e-6, LS=NP*P, XC=(ID+0.5)*P, WR=1.0e-6, HAL=100e-9, HLN=400e-9, HR=400e-9;
  static final double NO=2.211, NEX=2.138, N_M=1.44, K_M=16.0, N_OX=1.444, N_SI=3.476, LAM=1.55e-6, K0=2*Math.PI/LAM;
  static final double HAIRB=2e-6, HAIRT=2.5e-6, HSI=2e-6;
  static boolean FINE=false;

  public static void main(String[] args){
    try{
      ModelUtil.initStandalone(true);
      if(args!=null&&args.length>0) FINE="f".equals(args[0]);
      String sfx=FINE?"f":"";
      // tag, suspended, box thickness (m), fingers
      Object[][] cs={
        {"S0",true,0.0,false},
        {"SF",true,0.0,true},
        {"O2",false,2e-6,false},
        {"O1",false,1e-6,false},
        {"O4",false,4e-6,false}
      };
      for(Object[] c:cs) run((String)c[0]+sfx,(Boolean)c[1],(Double)c[2],(Boolean)c[3]);
    }catch(Throwable t){ System.out.println("STEP9_ABORT"); t.printStackTrace(System.out); }
  }

  static void run(String tag,boolean susp,double box,boolean fing)throws Exception{
    Model m=ModelUtil.create("M9");
    m.component().create("comp1",true);
    GeomSequence g=m.component("comp1").geom().create("geom1",2);
    g.lengthUnit("m");
    double yTop=HLN+HR+HAIRT;
    double yBot=susp?-HAIRB:-box-HSI;
    rect(g,"airT",0,HLN,LS,HR+HAIRT);
    rect(g,"rLn",0,0,LS,HLN);
    rect(g,"rRg",XC-WR/2,HLN,WR,HR);
    if(susp) rect(g,"airB",0,-HAIRB,LS,HAIRB);
    else{ rect(g,"oxB",0,-box,LS,box); rect(g,"siB",0,-box-HSI,LS,HSI); }
    if(fing){
      int na=0;
      int[][] grp={{0,DEF[0]-1},{DEF[DEF.length-1]+1,NP-1}};
      for(int[] gr:grp) for(int c=gr[0];c<=gr[1];c++){
        rect(g,"rA"+(na++),c*P+0.125*P,HLN,0.25*P,HAL);
        rect(g,"rA"+(na++),c*P+0.625*P,HLN,0.25*P,HAL);
      }
    }
    g.run();
    double t=1e-9;
    box(m,"selSlab",2,-t,LS+t,-t,HLN+t);
    box(m,"selRidge",2,XC-WR/2-t,XC+WR/2+t,HLN-t,HLN+HR+t);
    union(m,"selLN",new String[]{"selSlab","selRidge"});
    if(fing){
      box(m,"selAlL",2,-t,XC-WR/2-t,HLN-t,HLN+HAL+t);
      box(m,"selAlR",2,XC+WR/2+t,LS+t,HLN-t,HLN+HAL+t);
      union(m,"selAl",new String[]{"selAlL","selAlR"});
    }
    if(!susp){
      box(m,"selOx",2,-t,LS+t,-box-t,t);
      box(m,"selSi",2,-t,LS+t,-box-HSI-t,-box+t);
    }
    List<Integer> ext=new ArrayList<>();
    for(int e=1;e<=g.getNEdges();e++){
      double[][] q=g.edgeX(e,new double[]{0.0,0.5,1.0});
      double xm=q[1][0], ym=q[1][1];
      boolean ver=Math.abs(q[0][0]-q[2][0])<1e-11, hor=Math.abs(q[0][1]-q[2][1])<1e-11;
      if(ver&&(Math.abs(xm)<1e-11||Math.abs(xm-LS)<1e-11)) ext.add(e);
      else if(hor&&(Math.abs(ym-yBot)<1e-11||Math.abs(ym-yTop)<1e-11)) ext.add(e);
    }
    m.component("comp1").physics().create("ewfd","ElectromagneticWavesFrequencyDomain","geom1");
    Object w1=m.component("comp1").physics("ewfd").feature("wee1");
    sS(w1,"DisplacementFieldModel","RelativePermittivity");
    sS(w1,"epsilonr_mat","userdef"); sA(w1,"epsilonr",d3("1","1","1"));
    sS(w1,"mur_mat","userdef"); sA(w1,"mur",d3("1","1","1"));
    sS(w1,"sigma_mat","userdef"); sA(w1,"sigma",d3("0","0","0"));
    addWee(m,"weeLN","selLN",d3(""+NEX*NEX,""+NO*NO,""+NO*NO));
    if(!susp){
      addWee(m,"weeOx","selOx",d3(""+N_OX*N_OX,""+N_OX*N_OX,""+N_OX*N_OX));
      addWee(m,"weeSi","selSi",d3(""+N_SI*N_SI,""+N_SI*N_SI,""+N_SI*N_SI));
    }
    if(fing){
      m.component("comp1").physics("ewfd").create("weeAl","WaveEquationElectric",2);
      m.component("comp1").physics("ewfd").feature("weeAl").selection().named("selAl");
      Object w3=m.component("comp1").physics("ewfd").feature("weeAl");
      sS(w3,"DisplacementFieldModel","RefractiveIndex");
      sS(w3,"n_mat","userdef"); sA(w3,"n",d3(""+N_M,""+N_M,""+N_M));
      sS(w3,"ki_mat","userdef"); sA(w3,"ki",d3(""+K_M,""+K_M,""+K_M));
    }
    m.component("comp1").physics("ewfd").create("sctr1","Scattering",1);
    int[] ea=new int[ext.size()]; for(int i=0;i<ea.length;i++) ea[i]=ext.get(i);
    m.component("comp1").physics("ewfd").feature("sctr1").selection().set(ea);
    m.component("comp1").cpl().create("intAll","Integration");
    m.component("comp1").cpl("intAll").selection().geom("geom1",2);
    m.component("comp1").cpl("intAll").selection().all();
    m.param().set("xc",String.format(Locale.US,"%.10e[m]",XC));
    m.component("comp1").mesh().create("mesh1");
    m.component("comp1").mesh("mesh1").feature("size").set("custom","on");
    m.component("comp1").mesh("mesh1").feature("size").set("hmax",FINE?"70[nm]":"110[nm]");
    m.component("comp1").mesh("mesh1").feature("size").set("hmin","1[nm]");
    msize(m,"szLN","selLN",FINE?"14[nm]":"25[nm]");
    if(fing) msize(m,"szAl","selAl","10[nm]");
    m.component("comp1").mesh("mesh1").create("ftri1","FreeTri");
    m.component("comp1").mesh("mesh1").run();
    int nel=m.component("comp1").mesh("mesh1").getNumElem();

    String[] o1=optStudy(m,"stdO1",20,"1.950");
    double[] te=pickTE0(m,o1[1]);
    if(te==null){ System.out.println("TRANS9 case="+tag+" NO_TE0"); ModelUtil.remove("M9"); return; }
    String[] o2=optStudy(m,"stdO2",1,String.format(Locale.US,"%.8f",te[0]));
    double[] t2=modeRow(m,o2[1],0);
    System.out.println(String.format(Locale.US,"TRANS9 case=%s neff=%.8f imag_neff=%.4e dBcm=%.5f TEfrac=%.4f ridgeFrac=%.4f n_elem=%d susp=%b box_um=%.1f fingers=%b",
      tag,t2[0],t2[1],t2[2],t2[3],t2[4],nel,susp,box*1e6,fing));
    if(Math.abs(t2[0]-te[0])>1e-6||t2[3]<0.8){ System.out.println("TRANS9 case="+tag+" MODE_MISMATCH"); ModelUtil.remove("M9"); return; }
    String f="D:\\comsol_ao_run\\s9tr_"+tag+".txt";
    exportF(m,o2[1],f);
    System.out.println("TRANS9EXP case="+tag+" file="+f);
    ModelUtil.remove("M9");
  }

  static void exportF(Model m,String ds,String f){
    String[] q={"ewfd.Ex","ewfd.Ey","ewfd.Hx","ewfd.Hy"};
    String[] ex=new String[8];
    for(int i=0;i<4;i++){ ex[2*i]="real("+q[i]+")"; ex[2*i+1]="imag("+q[i]+")"; }
    double h=FINE?5e-9:1e-8;
    double x0=XC-3.5e-6+0.37*h, x1=XC+3.5e-6;
    double y0=-1.2e-6+0.41*h, y1=HLN+HR+1.2e-6;
    m.result().export().create("eopt","Data");
    m.result().export("eopt").set("data",ds);
    m.result().export("eopt").set("expr",ex);
    m.result().export("eopt").set("location","grid");
    m.result().export("eopt").set("gridx2",String.format(Locale.US,"range(%.10e,%.4e,%.10e)",x0,h,x1));
    m.result().export("eopt").set("gridy2",String.format(Locale.US,"range(%.10e,%.4e,%.10e)",y0,h,y1));
    m.result().export("eopt").set("header","off");
    m.result().export("eopt").set("filename",f);
    m.result().export("eopt").run();
  }

  static String[] d3(String a,String b,String c){ return new String[]{a,"0","0","0",b,"0","0","0",c}; }
  static void addWee(Model m,String tag,String sel,String[] eps)throws Exception{
    m.component("comp1").physics("ewfd").create(tag,"WaveEquationElectric",2);
    m.component("comp1").physics("ewfd").feature(tag).selection().named(sel);
    Object w=m.component("comp1").physics("ewfd").feature(tag);
    sS(w,"DisplacementFieldModel","RelativePermittivity");
    sS(w,"epsilonr_mat","userdef"); sA(w,"epsilonr",eps);
    sS(w,"mur_mat","userdef"); sA(w,"mur",d3("1","1","1"));
    sS(w,"sigma_mat","userdef"); sA(w,"sigma",d3("0","0","0"));
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
  static double[] pickTE0(Model m,String ds){
    double[][] v=evalG(m,ds,new String[]{"real(ewfd.neff)","imag(ewfd.neff)","intAll(abs(ewfd.Ex)^2)","intAll(ewfd.normE^2)","intAll(ewfd.normE^2*(abs(x-xc)<0.5[um]))"});
    double[] best=null;
    for(int k=0;k<v[0].length;k++){
      double te=v[2][k]/v[3][k], rf=v[4][k]/v[3][k];
      if(te>0.8&&(best==null||rf>best[4])) best=new double[]{v[0][k],v[1][k],0,te,rf};
    }
    if(best!=null&&best[4]<0.3) best=null;
    return best;
  }
  static double[][] evalG(Model m,String ds,String[] ex){
    m.result().numerical().create("gq","EvalGlobal");
    m.result().numerical("gq").set("data",ds);
    m.result().numerical("gq").set("expr",ex);
    m.result().numerical("gq").set("looplevelinput",new String[]{"all"});
    double[][] re=m.result().numerical("gq").getReal();
    m.result().numerical().remove("gq");
    return re;
  }
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
  static void msize(Model m,String t,String sel,String h){
    m.component("comp1").mesh("mesh1").create(t,"Size");
    m.component("comp1").mesh("mesh1").feature(t).selection().geom("geom1",2);
    m.component("comp1").mesh("mesh1").feature(t).selection().named(sel);
    m.component("comp1").mesh("mesh1").feature(t).set("custom","on");
    m.component("comp1").mesh("mesh1").feature(t).set("hmaxactive",true);
    m.component("comp1").mesh("mesh1").feature(t).set("hmax",h);
  }
  static void sS(Object o,String n,String v)throws Exception{ o.getClass().getMethod("set",String.class,String.class).invoke(o,n,v); }
  static void sA(Object o,String n,String[] v)throws Exception{ o.getClass().getMethod("set",String.class,String[].class).invoke(o,n,v); }
}
