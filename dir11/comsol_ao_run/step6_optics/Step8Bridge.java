import com.comsol.model.*;
import com.comsol.model.util.*;
import java.util.*;

/** Step 8: optical absorption of an Al air bridge over the suspended ridge (2D mode analysis, TE0 at 1550 nm).
 *  Cross-section as in Step7 comp1 (period 1.84 um, NP = 7, fingers removed in cells 2-4, ridge 1 um x 400 nm on a 400 nm slab,
 *  Al fingers 100 nm, n = 1.44 + 16i), plus an Al strip of width WBR and thickness TBR whose bottom is CL above the ridge top,
 *  spanning from the inner end of the left bus to the inner end of the right bus. Loss in dB/cm of the bridged section;
 *  per-bridge loss = alpha * (bridge length along the waveguide). CL < 0 means no bridge (reference). */
public class Step8Bridge {
  static final int NP=7, ID=3; static final int[] DEF={2,3,4};
  static final double P=1.84e-6, LS=NP*P, XC=(ID+0.5)*P, WR=1.0e-6, HAL=100e-9, HLN=400e-9, HR=400e-9;
  static final double NO=2.211, NEX=2.138, N_M=1.44, K_M=16.0, LAM=1.55e-6, K0=2*Math.PI/LAM;
  static final double HAIRB=2e-6;

  public static void main(String[] args){
    try{
      ModelUtil.initStandalone(true);
      double x0=(DEF[0]-1)*P+0.875*P, x1=(DEF[DEF.length-1]+1)*P+0.125*P;
      for(double tb:new double[]{100e-9,500e-9})
        for(double cl:new double[]{-1,0.5e-6,1e-6,1.5e-6,2e-6,3e-6}){
          if(tb>200e-9&&cl<0) continue;
          run(cl,tb,x0,x1);
        }
    }catch(Throwable t){ System.out.println("STEP8B_ABORT"); t.printStackTrace(System.out); }
  }

  static void run(double cl,double tb,double x0,double x1)throws Exception{
    Model m=ModelUtil.create("M8b");
    m.component().create("c1",true);
    GeomSequence g=m.component("c1").geom().create("g1",2);
    g.lengthUnit("m");
    double hTop=HR+Math.max(cl,0)+tb+2.5e-6;
    rect(g,"airB",0,-HAIRB,LS,HAIRB);
    rect(g,"airT",0,HLN,LS,hTop);
    rect(g,"rLn",0,0,LS,HLN);
    rect(g,"rRg",XC-WR/2,HLN,WR,HR);
    int na=0;
    int[][] grp={{0,DEF[0]-1},{DEF[DEF.length-1]+1,NP-1}};
    for(int[] gr:grp) for(int c=gr[0];c<=gr[1];c++){
      rect(g,"rA"+(na++),c*P+0.125*P,HLN,0.25*P,HAL);
      rect(g,"rA"+(na++),c*P+0.625*P,HLN,0.25*P,HAL);
    }
    if(cl>=0) rect(g,"rBr",x0,HLN+HR+cl,x1-x0,tb);
    g.run();
    double t=1e-9;
    box(m,"selSlab",2,-t,LS+t,-t,HLN+t);
    box(m,"selRidge",2,XC-WR/2-t,XC+WR/2+t,HLN-t,HLN+HR+t);
    uni(m,"selLN",new String[]{"selSlab","selRidge"});
    box(m,"selAlL",2,-t,XC-WR/2-t,HLN-t,HLN+HAL+t);
    box(m,"selAlR",2,XC+WR/2+t,LS+t,HLN-t,HLN+HAL+t);
    List<String> al=new ArrayList<>(Arrays.asList("selAlL","selAlR"));
    if(cl>=0){ box(m,"selBr",2,x0-t,x1+t,HLN+HR+cl-t,HLN+HR+cl+tb+t); al.add("selBr"); }
    uni(m,"selAl",al.toArray(new String[0]));
    List<Integer> ext=new ArrayList<>();
    for(int e=1;e<=g.getNEdges();e++){
      double[][] q=g.edgeX(e,new double[]{0.0,0.5,1.0});
      double xm=q[1][0], ym=q[1][1];
      boolean ver=Math.abs(q[0][0]-q[2][0])<1e-11, hor=Math.abs(q[0][1]-q[2][1])<1e-11;
      if(ver&&(Math.abs(xm)<1e-11||Math.abs(xm-LS)<1e-11)) ext.add(e);
      else if(hor&&(Math.abs(ym+HAIRB)<1e-11||Math.abs(ym-HLN-hTop)<1e-11)) ext.add(e);
    }
    m.component("c1").physics().create("ewfd","ElectromagneticWavesFrequencyDomain","g1");
    Object w1=m.component("c1").physics("ewfd").feature("wee1");
    sS(w1,"DisplacementFieldModel","RelativePermittivity");
    sS(w1,"epsilonr_mat","userdef"); sA(w1,"epsilonr",d3("1","1","1"));
    sS(w1,"mur_mat","userdef"); sA(w1,"mur",d3("1","1","1"));
    sS(w1,"sigma_mat","userdef"); sA(w1,"sigma",d3("0","0","0"));
    m.component("c1").physics("ewfd").create("weeLN","WaveEquationElectric",2);
    m.component("c1").physics("ewfd").feature("weeLN").selection().named("selLN");
    Object w2=m.component("c1").physics("ewfd").feature("weeLN");
    sS(w2,"DisplacementFieldModel","RelativePermittivity");
    sS(w2,"epsilonr_mat","userdef"); sA(w2,"epsilonr",d3(""+NEX*NEX,""+NO*NO,""+NO*NO));
    sS(w2,"mur_mat","userdef"); sA(w2,"mur",d3("1","1","1"));
    sS(w2,"sigma_mat","userdef"); sA(w2,"sigma",d3("0","0","0"));
    m.component("c1").physics("ewfd").create("weeAl","WaveEquationElectric",2);
    m.component("c1").physics("ewfd").feature("weeAl").selection().named("selAl");
    Object w3=m.component("c1").physics("ewfd").feature("weeAl");
    sS(w3,"DisplacementFieldModel","RefractiveIndex");
    sS(w3,"n_mat","userdef"); sA(w3,"n",d3(""+N_M,""+N_M,""+N_M));
    sS(w3,"ki_mat","userdef"); sA(w3,"ki",d3(""+K_M,""+K_M,""+K_M));
    m.component("c1").physics("ewfd").create("sctr1","Scattering",1);
    int[] ea=new int[ext.size()]; for(int i=0;i<ea.length;i++) ea[i]=ext.get(i);
    m.component("c1").physics("ewfd").feature("sctr1").selection().set(ea);
    m.component("c1").cpl().create("intAll","Integration");
    m.component("c1").cpl("intAll").selection().geom("g1",2);
    m.component("c1").cpl("intAll").selection().all();
    m.param().set("xc",String.format(Locale.US,"%.10e[m]",XC));
    m.component("c1").mesh().create("mesh1");
    m.component("c1").mesh("mesh1").feature("size").set("custom","on");
    m.component("c1").mesh("mesh1").feature("size").set("hmax","150[nm]");
    m.component("c1").mesh("mesh1").feature("size").set("hmin","1[nm]");
    msize(m,"szLN","selLN","30[nm]");
    msize(m,"szAl","selAl","10[nm]");
    m.component("c1").mesh("mesh1").create("ftri1","FreeTri");
    m.component("c1").mesh("mesh1").run();

    m.study().create("st");
    m.study("st").create("mode","ModeAnalysis");
    m.study("st").feature("mode").set("modeFreq","c_const/1.55[um]");
    m.study("st").feature("mode").set("neigsactive",true);
    m.study("st").feature("mode").set("neigs",20);
    m.study("st").feature("mode").set("shiftactive",true);
    m.study("st").feature("mode").set("shift","1.93");
    m.study("st").run();
    m.result().dataset().create("ds","Solution");
    m.result().numerical().create("gq","EvalGlobal");
    m.result().numerical("gq").set("data","ds");
    m.result().numerical("gq").set("expr",new String[]{"real(ewfd.neff)","imag(ewfd.neff)","intAll(abs(ewfd.Ex)^2)","intAll(ewfd.normE^2)","intAll(ewfd.normE^2*(abs(x-xc)<0.5[um]))"});
    m.result().numerical("gq").set("looplevelinput",new String[]{"all"});
    double[][] v=m.result().numerical("gq").getReal();
    int best=-1;
    for(int k=0;k<v[0].length;k++){
      double te=v[2][k]/v[3][k], rf=v[4][k]/v[3][k];
      if(te>0.8&&rf>0.3&&(best<0||rf>v[4][best]/v[3][best])) best=k;
    }
    if(best<0){ System.out.println(String.format(Locale.US,"BRIDGE8 cl_um=%.2f tb_nm=%.0f NO_TE0",cl*1e6,tb*1e9)); ModelUtil.remove("M8b"); return; }
    double ni=Math.abs(v[1][best]), dBcm=8.686*K0*ni/100;
    System.out.println(String.format(Locale.US,"BRIDGE8 cl_um=%.2f tb_nm=%.0f span_um=%.3f neff=%.6f imag_neff=%.4e dBcm=%.5f dB_per_um=%.3e TEfrac=%.4f ridgeFrac=%.4f n_elem=%d",
      cl*1e6,tb*1e9,(x1-x0)*1e6,v[0][best],ni,dBcm,dBcm*1e-4,v[2][best]/v[3][best],v[4][best]/v[3][best],m.component("c1").mesh("mesh1").getNumElem()));
    ModelUtil.remove("M8b");
  }
  static String[] d3(String a,String b,String c){ return new String[]{a,"0","0","0",b,"0","0","0",c}; }
  static void rect(GeomSequence g,String t,double x,double y,double w,double h){
    g.create(t,"Rectangle");
    g.feature(t).set("size",new String[]{String.format(Locale.US,"%.12e",w),String.format(Locale.US,"%.12e",h)});
    g.feature(t).set("pos",new String[]{String.format(Locale.US,"%.12e",x),String.format(Locale.US,"%.12e",y)});
  }
  static void box(Model m,String t,int dim,double xa,double xb,double ya,double yb){
    m.component("c1").selection().create(t,"Box");
    m.component("c1").selection(t).set("entitydim",""+dim);
    m.component("c1").selection(t).set("condition","inside");
    m.component("c1").selection(t).set("xmin",String.format(Locale.US,"%.12e",xa)); m.component("c1").selection(t).set("xmax",String.format(Locale.US,"%.12e",xb));
    m.component("c1").selection(t).set("ymin",String.format(Locale.US,"%.12e",ya)); m.component("c1").selection(t).set("ymax",String.format(Locale.US,"%.12e",yb));
  }
  static void uni(Model m,String t,String[] in){
    m.component("c1").selection().create(t,"Union");
    m.component("c1").selection(t).set("entitydim","2");
    m.component("c1").selection(t).set("input",in);
  }
  static void msize(Model m,String t,String sel,String h){
    m.component("c1").mesh("mesh1").create(t,"Size");
    m.component("c1").mesh("mesh1").feature(t).selection().geom("g1",2);
    m.component("c1").mesh("mesh1").feature(t).selection().named(sel);
    m.component("c1").mesh("mesh1").feature(t).set("custom","on");
    m.component("c1").mesh("mesh1").feature(t).set("hmaxactive",true);
    m.component("c1").mesh("mesh1").feature(t).set("hmax",h);
  }
  static void sS(Object o,String n,String v)throws Exception{ o.getClass().getMethod("set",String.class,String.class).invoke(o,n,v); }
  static void sA(Object o,String n,String[] v)throws Exception{ o.getClass().getMethod("set",String.class,String[].class).invoke(o,n,v); }
}
