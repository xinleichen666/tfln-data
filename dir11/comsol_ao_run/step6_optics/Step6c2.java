import com.comsol.model.*;
import com.comsol.model.util.*;
import java.util.*;

public class Step6c2 {
  static final double P=2.8526131500;
  static final int NP=7, ID=3;
  static final double HLN=0.5, HAL=0.1, WR=1.0, WT=0.9, HAIR=2.0, HW=6.0, LAM_UM=1.55;
  static final double NO=2.211, NE=2.138, N_AL=1.44, K_AL=16.0;
  static final double TE_REF=1.9638, TM_REF=1.7432;
  static final double XC=(ID+0.5)*P;
  static final double K0=2*Math.PI/(LAM_UM*1e-6);
  static final double[] SHIFTS={1.9,1.7};
  static final int NEIGS=6;

  public static void main(String[] args){
    try{
      ModelUtil.initStandalone(true);
      System.out.println("STEP6C2_START");
      System.out.println(String.format(Locale.US,"CFG p_um=%.8f xc_um=%.6f window_um=[%.6f,%.6f] hLN=%.3f hAl=%.3f wr=%.3f wt=%.3f hAir=%.1f lam_um=%.3f nO=%.3f nE=%.3f nAl=%.2f kAl=%.2f",
        P,XC,XC-HW,XC+HW,HLN,HAL,WR,WT,HAIR,LAM_UM,NO,NE,N_AL,K_AL));
      double[] s=solve(0,false,true);
      double dTE=Math.abs(s[0]-TE_REF)/TE_REF, dTM=Math.abs(s[3]-TM_REF)/TM_REF;
      boolean ok=dTE<=0.005&&dTM<=0.005;
      System.out.println(String.format(Locale.US,"SELFCHECK TE0_neff=%.6f ref=%.4f dev=%.3e TM0_neff=%.6f ref=%.4f dev=%.3e ok=%b",s[0],TE_REF,dTE,s[3],TM_REF,dTM,ok));
      if(!ok){ System.out.println("STEP6C2_STOP selfcheck deviation > 0.5%"); return; }
      double[] dts={50,100,150,200};
      for(double dT:dts) solve(dT,true,false);
      System.out.println("STEP6C2_DONE");
    }catch(Throwable t){ System.out.println("STEP6C2_ABORT"); t.printStackTrace(System.out); }
  }

  static double[] solve(double dTnm,boolean al,boolean self)throws Exception{
    String tag=self?"M6c2self":"M6c2_"+(int)dTnm;
    Model m=ModelUtil.create(tag);
    m.component().create("comp1",true);
    GeomSequence g=m.component("comp1").geom().create("geom1",2);
    g.lengthUnit("um");
    m.param().set("xc",String.format(Locale.US,"%.8f[um]",XC));
    double x0=self?XC-0.1:XC-HW, x1=self?XC+0.1:XC+HW, dT=dTnm*1e-3;
    rect(g,"air",x0,-HAIR,x1-x0,HLN+2*HAIR);
    rect(g,"ln",x0,0,x1-x0,HLN);
    if(dT>0){
      rect(g,"t1",XC-WR/2-WT,HLN-dT,WT,dT);
      rect(g,"t2",XC+WR/2,HLN-dT,WT,dT);
      g.create("dif1","Difference");
      g.feature("dif1").selection("input").set(new String[]{"ln"});
      g.feature("dif1").selection("input2").set(new String[]{"t1","t2"});
    }
    int nAlRect=0;
    if(al){
      for(int c=0;c<NP;c++){
        if(c==ID) continue;
        double[] st={c*P+0.125*P,c*P+0.625*P};
        for(int j=0;j<2;j++){
          double a=Math.max(st[j],x0), b=Math.min(st[j]+0.25*P,x1);
          if(b-a<1e-4) continue;
          rect(g,"al"+c+"_"+j,a,HLN,b-a,HAL); nAlRect++;
        }
      }
    }
    g.run();
    box(m,"selLN",2,x0-0.01,x1+0.01,-0.001,HLN+0.001);
    box(m,"selAl",2,x0-0.01,x1+0.01,HLN-0.001,HLN+HAL+0.001);
    box(m,"selL",1,x0-0.001,x0+0.001,-HAIR-0.01,HLN+HAIR+0.01);
    box(m,"selR",1,x1-0.001,x1+0.001,-HAIR-0.01,HLN+HAIR+0.01);
    box(m,"selB",1,x0-0.01,x1+0.01,-HAIR-0.001,-HAIR+0.001);
    box(m,"selT",1,x0-0.01,x1+0.01,HLN+HAIR-0.001,HLN+HAIR+0.001);
    int nLN=m.component("comp1").selection("selLN").entities().length;
    int nAl=m.component("comp1").selection("selAl").entities().length;
    System.out.println(String.format(Locale.US,"GEOM6C2 dT_nm=%.0f self=%b nDom=%d nLN=%d nAl=%d nAlRect=%d nL=%d nR=%d nB=%d nT=%d",dTnm,self,
      g.getNDomains(),nLN,nAl,nAlRect,
      m.component("comp1").selection("selL").entities().length,m.component("comp1").selection("selR").entities().length,
      m.component("comp1").selection("selB").entities().length,m.component("comp1").selection("selT").entities().length));
    if(nLN<1||(al&&nAl!=nAlRect)||(!al&&nAl!=0)) throw new RuntimeException("domain selection mismatch");

    String no2=String.valueOf(NO*NO), ne2=String.valueOf(NE*NE);
    double er=N_AL*N_AL-K_AL*K_AL, ei=-2*N_AL*K_AL;
    String eAl=String.format(Locale.US,"%.6f%+.6f*i",er,ei);
    Material mAir=mat(m,"matAir",null,"1","1","1");
    Material mLN=mat(m,"matLN","selLN",no2,no2,ne2);
    if(al){
      Material mAl=mat(m,"matAl","selAl",eAl,eAl,eAl);
      mAl.propertyGroup().create("RefractiveIndex","RefractiveIndex");
      String n=String.valueOf(N_AL), k=String.valueOf(K_AL);
      mAl.propertyGroup("RefractiveIndex").set("n",new String[]{n,"0","0","0",n,"0","0","0",n});
      mAl.propertyGroup("RefractiveIndex").set("ki",new String[]{k,"0","0","0",k,"0","0","0",k});
    }

    m.component("comp1").physics().create("ewfd","ElectromagneticWavesFrequencyDomain","geom1");
    m.component("comp1").physics("ewfd").feature("wee1").set("DisplacementFieldModel","RelativePermittivity");
    if(al){
      m.component("comp1").physics("ewfd").create("wee2","WaveEquationElectric",2);
      m.component("comp1").physics("ewfd").feature("wee2").selection().named("selAl");
      m.component("comp1").physics("ewfd").feature("wee2").set("DisplacementFieldModel","RefractiveIndex");
    }
    m.component("comp1").physics("ewfd").create("sctr1","Scattering",1);
    if(self){
      m.component("comp1").physics("ewfd").feature("sctr1").selection().set(cat(ents(m,"selB"),ents(m,"selT")));
      m.component("comp1").physics("ewfd").create("pc1","PeriodicCondition",1);
      m.component("comp1").physics("ewfd").feature("pc1").selection().set(cat(ents(m,"selL"),ents(m,"selR")));
    } else {
      m.component("comp1").physics("ewfd").feature("sctr1").selection().set(cat(cat(ents(m,"selB"),ents(m,"selT")),cat(ents(m,"selL"),ents(m,"selR"))));
    }

    cpl(m,"intAll",null); cpl(m,"intLN","selLN"); if(al) cpl(m,"intAl","selAl");

    m.component("comp1").mesh().create("mesh1");
    m.component("comp1").mesh("mesh1").feature("size").set("custom","on");
    m.component("comp1").mesh("mesh1").feature("size").set("hmax","0.2[um]");
    m.component("comp1").mesh("mesh1").feature("size").set("hmin","0.001[um]");
    msize(m,"szLN","selLN","0.03[um]");
    if(al) msize(m,"szAl","selAl","0.008[um]");
    m.component("comp1").mesh("mesh1").create("ftri1","FreeTri");
    m.component("comp1").mesh("mesh1").run();
    System.out.println(String.format(Locale.US,"NUMELEM6C2 dT_nm=%.0f self=%b n_elem=%d",dTnm,self,m.component("comp1").mesh("mesh1").getNumElem()));

    m.study().create("std1");
    m.study("std1").create("mode","ModeAnalysis");
    m.study("std1").feature("mode").set("modeFreq","c_const/"+LAM_UM+"[um]");
    m.study("std1").feature("mode").set("neigsactive",true);
    m.study("std1").feature("mode").set("neigs",NEIGS);
    m.study("std1").feature("mode").set("shiftactive",true);
    m.study("std1").createAutoSequences("all");

    List<double[]> all=new ArrayList<double[]>();
    String lab=self?"0_noAl_periodic":String.format(Locale.US,"%.0f",dTnm);
    for(double sh:SHIFTS){
      m.study("std1").feature("mode").set("shift",String.valueOf(sh));
      m.study("std1").run();
      m.result().numerical().create("gv","EvalGlobal");
      m.result().numerical("gv").set("data","dset1");
      m.result().numerical("gv").set("expr",new String[]{
        "real(ewfd.neff)","imag(ewfd.neff)","ewfd.dampz",
        "intAll(abs(ewfd.Ex)^2)","intAll(ewfd.normE^2)",
        "intAll(ewfd.normE^2*(abs(x-xc)<0.5[um]))","intLN(ewfd.normE^2*(abs(x-xc)<0.5[um]))"});
      m.result().numerical("gv").set("looplevelinput",new String[]{"all"});
      double[][] v=m.result().numerical("gv").getReal();
      m.result().numerical().remove("gv");
      for(int k=0;k<v[0].length;k++){
        double nre=v[0][k], nim=v[1][k], dz=v[2][k], tot=v[4][k];
        double te=tot>0?v[3][k]/tot:-1, rf=tot>0?v[5][k]/tot:-1, rl=tot>0?v[6][k]/tot:-1;
        double db=8.686*K0*Math.abs(nim)/100, dbz=8.686*dz/100;
        all.add(new double[]{nre,db,rf,te});
        System.out.println(String.format(Locale.US,"MODE6C2 dT=%s search=%.1f k=%d neff_re=%.6f neff_im=%.4e dBcm=%.4f dBcm_dampz=%.4f TEfrac=%.4f ridgeFrac=%.4f ridgeLNFrac=%.4f",
          lab,sh,k,nre,nim,db,dbz,te,rf,rl));
      }
    }
    if(al&&dTnm==50){
      try{
        m.result().numerical().create("ge","EvalGlobal");
        m.result().numerical("ge").set("data","dset1");
        m.result().numerical("ge").set("expr",new String[]{"intAl(real(ewfd.epsilonrxx))/intAl(1)","intAl(imag(ewfd.epsilonrxx))/intAl(1)"});
        m.result().numerical("ge").set("looplevelinput",new String[]{"first"});
        double[][] e=m.result().numerical("ge").getReal();
        System.out.println(String.format(Locale.US,"EPSCHK_AL re=%.4f im=%.4f expect_re=%.4f expect_im=%.4f",e[0][0],e[1][0],er,ei));
      }catch(Throwable t){ System.out.println("EPSCHK_AL_FAILED "+t.getMessage()); }
    }
    double[] te=pick(all,true), tm=pick(all,false);
    System.out.println(String.format(Locale.US,"OPT6C dT=%s TE0_neff=%.6f TE0_dBcm=%.4f TE0_conf=%.4f TM0_neff=%.6f TM0_dBcm=%.4f TM0_conf=%.4f",
      lab,te[0],te[1],te[2],tm[0],tm[1],tm[2]));
    ModelUtil.remove(tag);
    return new double[]{te[0],te[1],te[2],tm[0],tm[1],tm[2]};
  }

  static double[] pick(List<double[]> all,boolean teMode){
    double[] b=null;
    for(double[] r:all){
      if(teMode?r[3]<=0.8:r[3]>=0.2) continue;
      if(b==null||r[2]>b[2]+1e-6||(Math.abs(r[2]-b[2])<=1e-6&&r[0]>b[0])) b=r;
    }
    return b==null?new double[]{Double.NaN,Double.NaN,Double.NaN}:b;
  }
  static void rect(GeomSequence g,String t,double x,double y,double w,double h){
    g.create(t,"Rectangle");
    g.feature(t).set("size",new String[]{fmt(w),fmt(h)});
    g.feature(t).set("pos",new String[]{fmt(x),fmt(y)});
  }
  static String fmt(double v){ return String.format(Locale.US,"%.9f",v); }
  static void box(Model m,String t,int dim,double xa,double xb,double ya,double yb){
    m.component("comp1").selection().create(t,"Box");
    m.component("comp1").selection(t).set("entitydim",""+dim);
    m.component("comp1").selection(t).set("condition","inside");
    m.component("comp1").selection(t).set("xmin",fmt(xa)); m.component("comp1").selection(t).set("xmax",fmt(xb));
    m.component("comp1").selection(t).set("ymin",fmt(ya)); m.component("comp1").selection(t).set("ymax",fmt(yb));
  }
  static int[] ents(Model m,String s){ return m.component("comp1").selection(s).entities(); }
  static int[] cat(int[] a,int[] b){ int[] u=new int[a.length+b.length]; System.arraycopy(a,0,u,0,a.length); System.arraycopy(b,0,u,a.length,b.length); return u; }
  static Material mat(Model m,String t,String sel,String exx,String eyy,String ezz){
    Material x=m.component("comp1").material().create(t,"Common");
    if(sel==null) x.selection().all(); else x.selection().named(sel);
    x.propertyGroup("def").set("relpermittivity",new String[]{exx,"0","0","0",eyy,"0","0","0",ezz});
    x.propertyGroup("def").set("relpermeability",new String[]{"1","0","0","0","1","0","0","0","1"});
    x.propertyGroup("def").set("electricconductivity",new String[]{"0","0","0","0","0","0","0","0","0"});
    return x;
  }
  static void cpl(Model m,String t,String sel){
    m.component("comp1").cpl().create(t,"Integration");
    m.component("comp1").cpl(t).selection().geom("geom1",2);
    if(sel==null) m.component("comp1").cpl(t).selection().all(); else m.component("comp1").cpl(t).selection().named(sel);
  }
  static void msize(Model m,String t,String sel,String h){
    m.component("comp1").mesh("mesh1").create(t,"Size");
    m.component("comp1").mesh("mesh1").feature(t).selection().geom("geom1",2);
    m.component("comp1").mesh("mesh1").feature(t).selection().named(sel);
    m.component("comp1").mesh("mesh1").feature(t).set("custom","on");
    m.component("comp1").mesh("mesh1").feature(t).set("hmaxactive",true);
    m.component("comp1").mesh("mesh1").feature(t).set("hmax",h);
  }
}
