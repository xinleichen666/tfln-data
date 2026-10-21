import com.comsol.model.*;
import com.comsol.model.util.*;
import java.util.*;
import java.util.Locale;

public class Step6c1b {
  static final String PZ="D:\\COMSOL63\\Multiphysics\\data\\comsol_piezo_lib.mph";
  static final String BASIC="D:\\COMSOL63\\Multiphysics\\data\\comsol_basic_material_lib.mph";
  static final double P_UM=2.8526131500;
  static int NP=7, ID=3;
  static final int NH=7;
  static final double WR_UM=1.0, WT_UM=0.9;
  static double DT_NM=200;
  static final double F_REF=3.329955, F_PICK=3.3393;

  public static void main(String[] args){
    try{
      ModelUtil.initStandalone(true);
      System.out.println("STEP6C1B_START");
      int[] nps={7,7,7,13};
      double[] dts={50,100,150,200};
      for(int r=0;r<nps.length;r++){
        NP=nps[r]; ID=NP/2; DT_NM=dts[r];
        String name=String.format(Locale.US,"V2_NP%d_dT%d",NP,(int)DT_NM);
        System.out.println(String.format(Locale.US,"CFG run=%s p_um=%.8f NP=%d ID=%d wr_um=%.3f wt_um=%.3f dT_nm=%.1f Ls_um=%.6f",name,P_UM,NP,ID,WR_UM,WT_UM,DT_NM,NP*P_UM));
        Model m=ModelUtil.create("M6c1b"+r);
        build(m,2);
        m.study("stdE").run();
        report(m,name);
        ModelUtil.remove("M6c1b"+r);
      }
      System.out.println("STEP6C1B_DONE");
    }catch(Throwable t){ System.out.println("STEP6C1B_ABORT"); t.printStackTrace(System.out); }
  }

  static void report(Model m,String name){
    List<String> ex=new ArrayList<String>();
    ex.add("freq");
    ex.add("intLN(solid.Ws)"); ex.add("intAl(solid.Ws)");
    ex.add("intLN(abs(u)^2)"); ex.add("intLN(abs(v)^2)"); ex.add("intLN(abs(w)^2)");
    ex.add("intLN(abs(v)^2*(x>="+ID+"*p)*(x<"+(ID+1)+"*p))");
    ex.add("intBot(abs(v)^2)");
    for(int n=-NH;n<=NH;n++) ex.add("intBot(v*exp(-i*2*pi*("+n+")*x/p))");
    m.result().numerical().create("gev","EvalGlobal");
    m.result().numerical("gev").set("expr",ex.toArray(new String[0]));
    m.result().numerical("gev").set("looplevelinput",new String[]{"all"});
    double[][] re=m.result().numerical("gev").getReal();
    double[][] im=m.result().numerical("gev").getImag();
    int nm=re[0].length;
    double Ls=NP*P_UM*1e-6;
    int best=-1; double bestD=1e9;
    double[] fA=new double[nm], pvA=new double[nm], pfA=new double[nm];
    for(int k=0;k<nm;k++){
      double f=re[0][k]/1e9, fi=im[0][k]/1e9;
      double eL=Math.abs(re[1][k]), eA=Math.abs(re[2][k]);
      double u2=re[3][k], v2=re[4][k], w2=re[5][k], ut=u2+v2+w2;
      double pv=ut>0?v2/ut:-1;
      double fracAl=(eL+eA)>0?eA/(eL+eA):-1;
      double defect=v2>0?re[6][k]/(v2/NP):-1;
      double sc=0;
      for(int n=0;n<2*NH+1;n++){ double a=re[8+n][k], b=im[8+n][k]; sc+=a*a+b*b; }
      double pfrac=re[7][k]>0?sc/(Ls*re[7][k]):-1;
      double q=fi!=0?f/(2*Math.abs(fi)):-1;
      System.out.println(String.format(Locale.US,"MODE6C variant=%s k=%d f_GHz=%.6f Q=%.1f pv=%.3f fracAl=%.4f Pfrac=%.4f defectRatio=%.3f",name,k,f,q,pv,fracAl,pfrac,defect));
      fA[k]=f; pvA[k]=pv; pfA[k]=pfrac;
      if(f>3.30&&f<3.36&&pv>=0.8&&Math.abs(f-F_PICK)<bestD){ bestD=Math.abs(f-F_PICK); best=k; }
    }
    if(best>=0){
      double f=fA[best], sh=(f-F_REF)/F_REF;
      System.out.println(String.format(Locale.US,"TARGET6C variant=%s k=%d f_GHz=%.6f Pfrac=%.4f shift_rel=%.6e",name,best,f,pfA[best],sh));
      int nSplit=0;
      for(int k=0;k<nm;k++){
        if(k==best||Math.abs(fA[k]-f)>0.020||pvA[k]<0.5||pfA[k]<=0.3) continue;
        nSplit++;
        System.out.println(String.format(Locale.US,"SPLIT6C variant=%s k=%d f_GHz=%.6f df_MHz=%.2f pv=%.3f Pfrac=%.4f",name,k,fA[k],(fA[k]-f)*1e3,pvA[k],pfA[k]));
      }
      boolean ok=Math.abs(sh)<=0.005&&pfA[best]>0.9&&nSplit==0;
      System.out.println(String.format(Locale.US,"PASS6C1B variant=%s shiftOK=%b PfracOK=%b nSplit=%d pass=%b",name,Math.abs(sh)<=0.005,pfA[best]>0.9,nSplit,ok));
    } else System.out.println("TARGET6C variant="+name+" NONE");
    m.result().numerical().remove("gev");
  }

  static void build(Model m,int variant)throws Exception{
    m.param().set("p",String.format(Locale.US,"%.10f[um]",P_UM));
    m.param().set("hLn","500[nm]"); m.param().set("hAl","100[nm]"); m.param().set("duty","0.25");
    m.param().set("Ls",NP+"*p");
    m.param().set("wr",String.format(Locale.US,"%.4f[um]",WR_UM));
    m.param().set("wt",String.format(Locale.US,"%.4f[um]",WT_UM));
    m.param().set("dT",String.format(Locale.US,"%.2f[nm]",DT_NM));
    m.param().set("xc",(ID+0.5)+"*p");
    m.modelNode().create("comp1"); m.geom().create("geom1",2); m.geom("geom1").lengthUnit("m");
    rect(m,"rLn","Ls","hLn","0","0");
    if(variant==2){
      rect(m,"rT1","wt","dT","xc-wr/2-wt","hLn-dT");
      rect(m,"rT2","wt","dT","xc+wr/2","hLn-dT");
      m.geom("geom1").feature().create("dif1","Difference");
      m.geom("geom1").feature("dif1").selection("input").set(new String[]{"rLn"});
      m.geom("geom1").feature("dif1").selection("input2").set(new String[]{"rT1","rT2"});
    }
    for(int c=0;c<NP;c++){
      if(variant>=1&&c==ID) continue;
      rect(m,"rAp"+c,"duty*p","hAl",c+"*p+(p-2*duty*p)/4","hLn");
      rect(m,"rAn"+c,"duty*p","hAl",c+"*p+p/2+(p-2*duty*p)/4","hLn");
    }
    m.geom("geom1").run();
    box(m,"selLN",2,"1[nm]","Ls-1[nm]","1[nm]","hLn-1[nm]","intersects");
    box(m,"selAl",2,"1[nm]","Ls-1[nm]","hLn+1[nm]","hLn+hAl-1[nm]","intersects");
    box(m,"selBot",1,"-1[nm]","Ls+1[nm]","-1[nm]","1[nm]","inside");
    int[][] fe=fingerEdges(m,variant);
    System.out.println(String.format(Locale.US,"FINGER_CHECK variant=%d nTerm=%d nGnd=%d expect=%d nAl=%d nBot=%d",variant,fe[0].length,fe[1].length,variant>=1?NP-1:NP,
      m.component("comp1").selection("selAl").entities().length,m.component("comp1").selection("selBot").entities().length));
    if(fe[0].length!=(variant>=1?NP-1:NP)||fe[1].length!=fe[0].length) throw new RuntimeException("finger edge count mismatch");
    Model pz=ModelUtil.load("pz",PZ); Model bs=ModelUtil.load("basic",BASIC);
    Material ln=m.component("comp1").material().create("matLN","Common"); ln.selection().named("selLN");
    copyGroup(ln,pz.material("lithium_niobate"),"def",false); copyGroup(ln,pz.material("lithium_niobate"),"StressCharge",true);
    Material al=m.component("comp1").material().create("matAl","Common"); al.selection().named("selAl");
    copyGroup(al,bs.material("aluminum"),"def",false); copyGroup(al,bs.material("aluminum"),"Enu",true);
    ModelUtil.remove("pz"); ModelUtil.remove("basic");
    m.physics().create("solid","SolidMechanics","geom1"); m.physics().create("es","Electrostatics","geom1"); m.physics("es").selection().named("selLN");
    m.physics("solid").create("pzm1","PiezoelectricMaterialModel",2); m.physics("solid").feature("pzm1").selection().named("selLN");
    m.multiphysics().create("pze1","PiezoelectricEffect","geom1");
    m.physics("es").create("ccp1","ChargeConservationPiezo",2); m.physics("es").feature("ccp1").selection().named("selLN");
    Object sys=m.component("comp1").coordSystem().create("sys2","Rotated"); sS(sys,"rotationSequence","ZXZ"); sA(sys,"angle",new String[]{"90[deg]","0","0"});
    sS(m.physics("solid").feature("pzm1"),"coordinateSystem","sys2"); sS(m.physics("es").feature("ccp1"),"coordinateSystem","sys2");
    m.physics("solid").feature("pzm1").create("dmp1","Damping",2);
    m.physics("solid").feature("pzm1").feature("dmp1").set("DampingType","IsotropicLossFactor");
    m.physics("solid").feature("pzm1").feature("dmp1").set("eta_s_mat","userdef");
    m.physics("solid").feature("pzm1").feature("dmp1").set("eta_s","5e-4");
    m.physics("es").create("gndT","Ground",1); m.physics("es").feature("gndT").selection().set(fe[0]);
    m.physics("es").create("gnd1","Ground",1); m.physics("es").feature("gnd1").selection().set(fe[1]);
    m.physics("solid").create("pc1","PeriodicCondition",1); m.physics("es").create("pc1","PeriodicCondition",1);
    m.physics("solid").feature("pc1").selection().set(sideE(m,false)); m.physics("es").feature("pc1").selection().set(sideE(m,true));
    Object pr=m.physics("solid").prop("Type2D"); sS(pr,"ModeExtension","1"); sS(pr,"kz","0");
    m.component("comp1").cpl().create("intLN","Integration"); m.component("comp1").cpl("intLN").selection().geom("geom1",2); m.component("comp1").cpl("intLN").selection().named("selLN");
    m.component("comp1").cpl().create("intAl","Integration"); m.component("comp1").cpl("intAl").selection().geom("geom1",2); m.component("comp1").cpl("intAl").selection().named("selAl");
    m.component("comp1").cpl().create("intBot","Integration"); m.component("comp1").cpl("intBot").selection().geom("geom1",1); m.component("comp1").cpl("intBot").selection().named("selBot");
    m.mesh().create("mesh1","geom1");
    m.mesh("mesh1").feature().create("szLN","Size"); m.mesh("mesh1").feature("szLN").selection().geom("geom1",2); m.mesh("mesh1").feature("szLN").selection().named("selLN");
    m.mesh("mesh1").feature("szLN").set("hmaxactive","on"); m.mesh("mesh1").feature("szLN").set("hmax","40[nm]");
    m.mesh("mesh1").feature().create("ftri1","FreeTri"); m.mesh("mesh1").feature("ftri1").selection().geom("geom1",2); m.mesh("mesh1").feature("ftri1").selection().all();
    m.mesh("mesh1").run();
    System.out.println("NUMELEM variant="+variant+" n_elem="+m.mesh("mesh1").getNumElem());
    m.study().create("stdE"); m.study("stdE").create("eig","Eigenfrequency");
    m.study("stdE").feature("eig").set("neigs","40");
    m.study("stdE").feature("eig").set("shift","3.33[GHz]");
    m.study("stdE").feature("eig").set("shiftactive","on");
    m.study("stdE").createAutoSequences("all");
  }

  static int[][] fingerEdges(Model m,int variant){
    double p=P_UM*1e-6, h=500e-9, a=(p-2*0.25*p)/4, w=0.25*p;
    int nE=m.geom("geom1").getNEdges();
    List<Integer> t=new ArrayList<Integer>(), g=new ArrayList<Integer>();
    for(int e=1;e<=nE;e++){
      double[][] q=m.geom("geom1").edgeX(e,new double[]{0.0,0.5,1.0});
      if(Math.abs(q[0][1]-h)>1e-10||Math.abs(q[2][1]-h)>1e-10) continue;
      double xm=q[1][0], xl=Math.min(q[0][0],q[2][0]), xr=Math.max(q[0][0],q[2][0]);
      int c=(int)Math.floor(xm/p);
      if(c<0||c>=NP) continue;
      if(variant>=1&&c==ID) continue;
      double x0=xm-c*p;
      if(x0>a&&x0<a+w&&Math.abs((xr-xl)-w)<1e-10) t.add(e);
      else if(x0>p/2+a&&x0<p/2+a+w&&Math.abs((xr-xl)-w)<1e-10) g.add(e);
    }
    int[][] r=new int[2][];
    r[0]=new int[t.size()]; for(int i=0;i<t.size();i++) r[0][i]=t.get(i);
    r[1]=new int[g.size()]; for(int i=0;i<g.size();i++) r[1][i]=g.get(i);
    return r;
  }
  static int[] sideE(Model m,boolean ln){
    int nE=m.geom("geom1").getNEdges(); int[] L=new int[nE],R=new int[nE]; int nl=0,nr=0; double pm=0;
    for(int e=1;e<=nE;e++){ double[][] a=m.geom("geom1").edgeX(e,new double[]{0.5}); pm=Math.max(pm,a[0][0]); }
    for(int e=1;e<=nE;e++){
      double[][] a=m.geom("geom1").edgeX(e,new double[]{0.02,0.98});
      double x0=a[0][0],y0=a[0][1],x1=a[1][0],y1=a[1][1];
      if(Math.abs(x0-x1)>1e-10||Math.abs(y0-y1)<1e-10) continue;
      double yl=Math.min(y0,y1),yh=Math.max(y0,y1);
      if(ln&&(yl<-1e-9||yh>500e-9+1e-9)) continue;
      if(Math.abs(x0)<1e-9) L[nl++]=e;
      if(Math.abs(x0-pm)<1e-9) R[nr++]=e;
    }
    int[] u=new int[nl+nr]; System.arraycopy(L,0,u,0,nl); System.arraycopy(R,0,u,nl,nr); return u;
  }
  static void rect(Model m,String t,String sx,String sy,String px,String py){
    m.geom("geom1").feature().create(t,"Rectangle");
    m.geom("geom1").feature(t).set("size",new String[]{sx,sy});
    m.geom("geom1").feature(t).set("pos",new String[]{px,py});
  }
  static void box(Model m,String t,int dim,String x0,String x1,String y0,String y1,String cond){
    m.component("comp1").selection().create(t,"Box");
    m.component("comp1").selection(t).set("entitydim",""+dim);
    m.component("comp1").selection(t).set("condition",cond);
    m.component("comp1").selection(t).set("xmin",x0); m.component("comp1").selection(t).set("xmax",x1);
    m.component("comp1").selection(t).set("ymin",y0); m.component("comp1").selection(t).set("ymax",y1);
  }
  static void copyGroup(Material d,Material s,String g,boolean c){
    if(c) d.propertyGroup().create(g,g);
    String[] n=s.propertyGroup(g).properties();
    for(int i=0;i<n.length;i++){ try{ d.propertyGroup(g).set(n[i],s.propertyGroup(g).getStringArray(n[i])); }catch(Exception e){} }
  }
  static void sS(Object o,String n,String v)throws Exception{ o.getClass().getMethod("set",String.class,String.class).invoke(o,n,v); }
  static void sA(Object o,String n,String[] v)throws Exception{ o.getClass().getMethod("set",String.class,String[].class).invoke(o,n,v); }
}
