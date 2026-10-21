import com.comsol.model.*;
import com.comsol.model.util.*;
import java.util.*;

public class Step6c2b {
  static final double P=2.8526131500;
  static final int NP=7, ID=3;
  static final double HLN=0.5, HAL=0.1, WR=1.0, HAIR=2.0, HW=6.0, LAM_UM=1.55;
  static final double NO=2.211, NE=2.138, N_AL=1.44, K_AL=16.0;
  static final double TE_REF=1.9638;
  static final double XC=(ID+0.5)*P;
  static final double K0=2*Math.PI/(LAM_UM*1e-6);
  static final double SHIFT=1.92;
  static final int NEIGS=10;

  public static void main(String[] args){
    try{
      ModelUtil.initStandalone(true);
      System.out.println("STEP6C2B_START");
      System.out.println(String.format(Locale.US,"CFG p_um=%.8f xc_um=%.6f window_um=[%.6f,%.6f] hLN=%.3f hAl=%.3f wr=%.3f hAir=%.1f lam_um=%.3f nO=%.3f nE=%.3f nAl=%.2f kAl=%.2f shift=%.2f neigs=%d",
        P,XC,XC-HW,XC+HW,HLN,HAL,WR,HAIR,LAM_UM,NO,NE,N_AL,K_AL,SHIFT,NEIGS));
      double[] s=solve(500,0,true);
      double dTE=Math.abs(s[0]-TE_REF)/TE_REF;
      boolean ok=dTE<=0.005;
      System.out.println(String.format(Locale.US,"SELFCHECK TE0_neff=%.6f ref=%.4f dev=%.3e ok=%b",s[0],TE_REF,dTE,ok));
      if(!ok){ System.out.println("STEP6C2B_STOP selfcheck deviation > 0.5%"); return; }
      double[] hss={350,400,450};
      int[] nds={1,3};
      for(double hs:hss) for(int nd:nds) solve(hs,nd,false);
      System.out.println("STEP6C2B_DONE");
    }catch(Throwable t){ System.out.println("STEP6C2B_ABORT"); t.printStackTrace(System.out); }
  }

  static double[] solve(double hsNm,int ndef,boolean self)throws Exception{
    String tag=self?"M6c2bself":"M6c2b_"+(int)hsNm+"_"+ndef;
    Model m=ModelUtil.create(tag);
    m.component().create("comp1",true);
    GeomSequence g=m.component("comp1").geom().create("geom1",2);
    g.lengthUnit("um");
    m.param().set("xc",String.format(Locale.US,"%.8f[um]",XC));
    double hs=hsNm*1e-3;
    double x0=self?XC-0.1:XC-HW, x1=self?XC+0.1:XC+HW;
    boolean ridge=!self&&hs<HLN-1e-6;
    rect(g,"air",x0,-HAIR,x1-x0,HLN+2*HAIR);
    rect(g,"slab",x0,0,x1-x0,hs);
    if(ridge) rect(g,"ridge",XC-WR/2,hs,WR,HLN-hs);
    int nAlRect=0;
    if(!self){
      for(int c=0;c<NP;c++){
        if(Math.abs(c-ID)<=(ndef-1)/2) continue;
        double[] st={c*P+0.125*P,c*P+0.625*P};
        for(int j=0;j<2;j++){
          double a=Math.max(st[j],x0), b=Math.min(st[j]+0.25*P,x1);
          if(b-a<1e-4) continue;
          if(b>XC-WR/2&&a<XC+WR/2) throw new RuntimeException("finger overlaps ridge c="+c);
          rect(g,"al"+c+"_"+j,a,hs,b-a,HAL); nAlRect++;
        }
      }
    }
    g.run();
    box(m,"selSlab",2,x0-0.01,x1+0.01,-0.001,hs+0.001);
    box(m,"selRidge",2,XC-WR/2-0.001,XC+WR/2+0.001,hs-0.001,HLN+0.001);
    union(m,"selLN",new String[]{"selSlab","selRidge"});
    box(m,"selAlL",2,x0-0.01,XC-WR/2-0.001,hs-0.001,hs+HAL+0.001);
    box(m,"selAlR",2,XC+WR/2+0.001,x1+0.01,hs-0.001,hs+HAL+0.001);
    union(m,"selAl",new String[]{"selAlL","selAlR"});
    box(m,"selL",1,x0-0.001,x0+0.001,-HAIR-0.01,HLN+HAIR+0.01);
    box(m,"selR",1,x1-0.001,x1+0.001,-HAIR-0.01,HLN+HAIR+0.01);
    box(m,"selB",1,x0-0.01,x1+0.01,-HAIR-0.001,-HAIR+0.001);
    box(m,"selT",1,x0-0.01,x1+0.01,HLN+HAIR-0.001,HLN+HAIR+0.001);
    int nLN=ents(m,"selLN").length, nAl=nAlRect>0?ents(m,"selAl").length:0;
    int expLN=ridge?2:1;
    System.out.println(String.format(Locale.US,"GEOM6C2B hs_nm=%.0f Ndef=%d self=%b nDom=%d nLN=%d expLN=%d nAl=%d nAlRect=%d nL=%d nR=%d nB=%d nT=%d",hsNm,ndef,self,
      g.getNDomains(),nLN,expLN,nAl,nAlRect,ents(m,"selL").length,ents(m,"selR").length,ents(m,"selB").length,ents(m,"selT").length));
    if(nLN!=expLN||nAl!=nAlRect) throw new RuntimeException("domain selection mismatch");

    String no2=String.valueOf(NO*NO), ne2=String.valueOf(NE*NE);
    double er=N_AL*N_AL-K_AL*K_AL, ei=-2*N_AL*K_AL;
    String eAl=String.format(Locale.US,"%.6f%+.6f*i",er,ei);
    mat(m,"matAir",null,"1","1","1");
    mat(m,"matLN","selLN",no2,no2,ne2);
    if(nAlRect>0){
      Material mAl=mat(m,"matAl","selAl",eAl,eAl,eAl);
      mAl.propertyGroup().create("RefractiveIndex","RefractiveIndex");
      String n=String.valueOf(N_AL), k=String.valueOf(K_AL);
      mAl.propertyGroup("RefractiveIndex").set("n",new String[]{n,"0","0","0",n,"0","0","0",n});
      mAl.propertyGroup("RefractiveIndex").set("ki",new String[]{k,"0","0","0",k,"0","0","0",k});
    }

    m.component("comp1").physics().create("ewfd","ElectromagneticWavesFrequencyDomain","geom1");
    m.component("comp1").physics("ewfd").feature("wee1").set("DisplacementFieldModel","RelativePermittivity");
    if(nAlRect>0){
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

    cpl(m,"intAll",null);

    m.component("comp1").mesh().create("mesh1");
    m.component("comp1").mesh("mesh1").feature("size").set("custom","on");
    m.component("comp1").mesh("mesh1").feature("size").set("hmax","0.2[um]");
    m.component("comp1").mesh("mesh1").feature("size").set("hmin","0.001[um]");
    msize(m,"szLN","selLN","0.03[um]");
    if(nAlRect>0) msize(m,"szAl","selAl","0.008[um]");
    m.component("comp1").mesh("mesh1").create("ftri1","FreeTri");
    m.component("comp1").mesh("mesh1").run();
    System.out.println(String.format(Locale.US,"NUMELEM6C2B hs_nm=%.0f Ndef=%d self=%b n_elem=%d",hsNm,ndef,self,m.component("comp1").mesh("mesh1").getNumElem()));

    m.study().create("std1");
    m.study("std1").create("mode","ModeAnalysis");
    m.study("std1").feature("mode").set("modeFreq","c_const/"+LAM_UM+"[um]");
    m.study("std1").feature("mode").set("neigsactive",true);
    m.study("std1").feature("mode").set("neigs",NEIGS);
    m.study("std1").feature("mode").set("shiftactive",true);
    m.study("std1").feature("mode").set("shift",String.valueOf(SHIFT));
    m.study("std1").createAutoSequences("all");
    m.study("std1").run();

    String lab=self?"hs=500 Ndef=0 noAl_periodic":String.format(Locale.US,"hs=%.0f Ndef=%d",hsNm,ndef);
    m.result().numerical().create("gv","EvalGlobal");
    m.result().numerical("gv").set("data","dset1");
    m.result().numerical("gv").set("expr",new String[]{
      "real(ewfd.neff)","imag(ewfd.neff)","ewfd.dampz",
      "intAll(abs(ewfd.Ex)^2)","intAll(ewfd.normE^2)",
      "intAll(ewfd.normE^2*(abs(x-xc)<0.5[um]))"});
    m.result().numerical("gv").set("looplevelinput",new String[]{"all"});
    double[][] v=m.result().numerical("gv").getReal();
    m.result().numerical().remove("gv");
    double[] best=null; int bestK=-1;
    for(int k=0;k<v[0].length;k++){
      double nre=v[0][k], nim=v[1][k], dz=v[2][k], tot=v[4][k];
      double te=tot>0?v[3][k]/tot:-1, rf=tot>0?v[5][k]/tot:-1;
      double db=8.686*K0*Math.abs(nim)/100, dbz=8.686*dz/100;
      System.out.println(String.format(Locale.US,"MODE6C2B %s k=%d neff_re=%.6f neff_im=%.4e dBcm=%.4f dBcm_dampz=%.4f TEfrac=%.4f ridgeFrac=%.4f",
        lab,k,nre,nim,db,dbz,te,rf));
      if(te<=0.8) continue;
      if(best==null||rf>best[2]+1e-6||(Math.abs(rf-best[2])<=1e-6&&nre>best[0])){ best=new double[]{nre,db,rf}; bestK=k; }
    }
    double[] r;
    if(best==null||best[2]<0.3){
      System.out.println(String.format(Locale.US,"OPT6C2B %s TE0=NONE maxRidgeFrac=%.4f",lab,best==null?-1:best[2]));
      r=new double[]{Double.NaN,Double.NaN,Double.NaN};
    } else {
      System.out.println(String.format(Locale.US,"OPT6C2B %s k=%d TE0_neff=%.6f TE0_dBcm=%.4f TE0_conf=%.4f",lab,bestK,best[0],best[1],best[2]));
      r=best;
    }
    ModelUtil.remove(tag);
    return r;
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
  static void union(Model m,String t,String[] in){
    m.component("comp1").selection().create(t,"Union");
    m.component("comp1").selection(t).set("entitydim","2");
    m.component("comp1").selection(t).set("input",in);
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
