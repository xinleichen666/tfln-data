import com.comsol.model.*;
import com.comsol.model.util.*;
import java.util.*;
import java.util.Locale;

public class Step6d2 {
  static final String PZ="D:\\COMSOL63\\Multiphysics\\data\\comsol_piezo_lib.mph";
  static final String BASIC="D:\\COMSOL63\\Multiphysics\\data\\comsol_basic_material_lib.mph";
  static final String SAVE="D:\\comsol_ao_run\\step6_optics\\step6d_geom.mph";
  static final double P_UM=2.71043685;
  static final double F_UNIT=3.329801, FA_T_UNIT=0.0608, FA_P_UNIT=0.0896;
  static final int NP=15, ID=7, NH=7;
  static final int[] DEF={6,7,8};
  static final double WR_UM=1.0, HLN_NM=400, HR_NM=100;

  public static void main(String[] args){
    try{
      ModelUtil.initStandalone(true);
      System.out.println("STEP6D2_START");
      System.out.println(String.format(Locale.US,"CFG p_um=%.8f NP=%d ID=%d def=%s hLn_nm=%.0f ridge_w_um=%.3f ridge_h_nm=%.0f Ls_um=%.6f F_UNIT=%.6f FA_T_UNIT=%.4f FA_P_UNIT=%.4f",
        P_UM,NP,ID,Arrays.toString(DEF),HLN_NM,WR_UM,HR_NM,NP*P_UM,F_UNIT,FA_T_UNIT,FA_P_UNIT));
      String[] names={"V1_def3_noRidge","V2_def3_ridge"};
      for(int v=0;v<2;v++){
        Model m=ModelUtil.create("M6d"+v);
        build(m,v==1);
        m.study("stdE").run();
        report(m,names[v]);
        if(v==1){ m.save(SAVE); System.out.println("SAVED "+SAVE); }
        ModelUtil.remove("M6d"+v);
      }
      System.out.println("STEP6D2_DONE");
    }catch(Throwable t){ System.out.println("STEP6D2_ABORT"); t.printStackTrace(System.out); }
  }

  static boolean isDef(int c){ for(int d:DEF) if(d==c) return true; return false; }

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
    double scale=(double)(NP-DEF.length)/NP, eT=FA_T_UNIT*scale, eP=FA_P_UNIT*scale;
    double[] fA=new double[nm], pvA=new double[nm], pfA=new double[nm], faA=new double[nm], dfA=new double[nm], qA=new double[nm];
    int best=-1; double bestD=1e9;
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
      fA[k]=f; pvA[k]=pv; pfA[k]=pfrac; faA[k]=fracAl; dfA[k]=defect; qA[k]=q;
      System.out.println(String.format(Locale.US,"MODE6D variant=%s k=%d f_GHz=%.6f Q=%.1f pv=%.3f fracAl=%.4f Pfrac=%.4f defectRatio=%.3f",name,k,f,q,pv,fracAl,pfrac,defect));
      if(f<3.20||f>3.46||pv<0.8) continue;
      if(Math.abs(fracAl-eT)>=Math.abs(fracAl-eP)) continue;
      if(Math.abs(fracAl-eT)<bestD){ bestD=Math.abs(fracAl-eT); best=k; }
    }
    System.out.println(String.format(Locale.US,"PICKRULE6D variant=%s window=[3.20,3.46] pv>=0.8 expect_fracAl_driven=%.4f expect_fracAl_partner=%.4f (unit-cell x %d/%d); pick = closer to driven, min |fracAl-driven|",name,eT,eP,NP-DEF.length,NP));
    if(best<0){ System.out.println("TARGET6D variant="+name+" NONE"); m.result().numerical().remove("gev"); return; }
    double f=fA[best];
    System.out.println(String.format(Locale.US,"TARGET6D variant=%s k=%d f_GHz=%.6f shift_vs_unit=%.6e Q=%.1f pv=%.3f fracAl=%.4f Pfrac=%.4f defectRatio=%.3f",
      name,best,f,(f-F_UNIT)/F_UNIT,qA[best],pvA[best],faA[best],pfA[best],dfA[best]));
    int nSplit=0;
    for(int k=0;k<nm;k++){
      if(k==best||Math.abs(fA[k]-f)>0.030||pvA[k]<0.5) continue;
      boolean sp=Math.abs(fA[k]-f)<=0.020&&pfA[k]>0.3;
      if(sp) nSplit++;
      System.out.println(String.format(Locale.US,"NEAR6D variant=%s k=%d f_GHz=%.6f df_MHz=%.2f pv=%.3f fracAl=%.4f Pfrac=%.4f defectRatio=%.3f split=%b",
        name,k,fA[k],(fA[k]-f)*1e3,pvA[k],faA[k],pfA[k],dfA[k],sp));
    }
    boolean ok=pfA[best]>0.9&&nSplit==0;
    System.out.println(String.format(Locale.US,"PASS6D variant=%s PfracOK=%b nSplit=%d pass=%b",name,pfA[best]>0.9,nSplit,ok));
    m.result().numerical().remove("gev");
  }

  static void build(Model m,boolean ridge)throws Exception{
    m.param().set("p",String.format(Locale.US,"%.10f[um]",P_UM));
    m.param().set("hLn",String.format(Locale.US,"%.1f[nm]",HLN_NM)); m.param().set("hAl","100[nm]"); m.param().set("duty","0.25");
    m.param().set("hR",String.format(Locale.US,"%.1f[nm]",HR_NM));
    m.param().set("Ls",NP+"*p");
    m.param().set("wr",String.format(Locale.US,"%.4f[um]",WR_UM));
    m.param().set("xc",(ID+0.5)+"*p");
    m.modelNode().create("comp1"); m.geom().create("geom1",2); m.geom("geom1").lengthUnit("m");
    rect(m,"rLn","Ls","hLn","0","0");
    if(ridge) rect(m,"rRg","wr","hR","xc-wr/2","hLn");
    for(int c=0;c<NP;c++){
      if(isDef(c)) continue;
      rect(m,"rAp"+c,"duty*p","hAl",c+"*p+(p-2*duty*p)/4","hLn");
      rect(m,"rAn"+c,"duty*p","hAl",c+"*p+p/2+(p-2*duty*p)/4","hLn");
    }
    m.geom("geom1").run();
    box(m,"selSlab",2,"1[nm]","Ls-1[nm]","1[nm]","hLn-1[nm]","intersects");
    box(m,"selRidge",2,"xc-wr/2+1[nm]","xc+wr/2-1[nm]","hLn+1[nm]","hLn+hR-1[nm]","intersects");
    union(m,"selLN",new String[]{"selSlab","selRidge"});
    box(m,"selAlL",2,"1[nm]","xc-wr/2-1[nm]","hLn+1[nm]","hLn+hAl-1[nm]","intersects");
    box(m,"selAlR",2,"xc+wr/2+1[nm]","Ls-1[nm]","hLn+1[nm]","hLn+hAl-1[nm]","intersects");
    union(m,"selAl",new String[]{"selAlL","selAlR"});
    box(m,"selBot",1,"-1[nm]","Ls+1[nm]","-1[nm]","1[nm]","inside");
    int[][] fe=fingerEdges(m);
    int nExp=NP-DEF.length;
    int nLN=m.component("comp1").selection("selLN").entities().length;
    int nAl=m.component("comp1").selection("selAl").entities().length;
    int nBot=m.component("comp1").selection("selBot").entities().length;
    System.out.println(String.format(Locale.US,"FINGER_CHECK ridge=%b nTerm=%d nGnd=%d expect=%d nAl=%d expectAl=%d nLN=%d expectLN=%d nBot=%d",
      ridge,fe[0].length,fe[1].length,nExp,nAl,2*nExp,nLN,ridge?2:1,nBot));
    if(fe[0].length!=nExp||fe[1].length!=nExp||nAl!=2*nExp||nLN!=(ridge?2:1)||nBot<1) throw new RuntimeException("selection count mismatch");
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
    System.out.println("NUMELEM ridge="+ridge+" n_elem="+m.mesh("mesh1").getNumElem());
    m.study().create("stdE"); m.study("stdE").create("eig","Eigenfrequency");
    m.study("stdE").feature("eig").set("neigs","60");
    m.study("stdE").feature("eig").set("shift","3.33[GHz]");
    m.study("stdE").feature("eig").set("shiftactive","on");
    m.study("stdE").createAutoSequences("all");
  }

  static int[][] fingerEdges(Model m){
    double p=P_UM*1e-6, h=HLN_NM*1e-9, a=(p-2*0.25*p)/4, w=0.25*p;
    int nE=m.geom("geom1").getNEdges();
    List<Integer> t=new ArrayList<Integer>(), g=new ArrayList<Integer>();
    for(int e=1;e<=nE;e++){
      double[][] q=m.geom("geom1").edgeX(e,new double[]{0.0,0.5,1.0});
      if(Math.abs(q[0][1]-h)>1e-10||Math.abs(q[2][1]-h)>1e-10) continue;
      double xm=q[1][0], xl=Math.min(q[0][0],q[2][0]), xr=Math.max(q[0][0],q[2][0]);
      int c=(int)Math.floor(xm/p);
      if(c<0||c>=NP||isDef(c)) continue;
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
      if(ln&&(yl<-1e-9||yh>HLN_NM*1e-9+1e-9)) continue;
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
  static void union(Model m,String t,String[] in){
    m.component("comp1").selection().create(t,"Union");
    m.component("comp1").selection(t).set("entitydim","2");
    m.component("comp1").selection(t).set("input",in);
  }
  static void copyGroup(Material d,Material s,String g,boolean c){
    if(c) d.propertyGroup().create(g,g);
    String[] n=s.propertyGroup(g).properties();
    for(int i=0;i<n.length;i++){ try{ d.propertyGroup(g).set(n[i],s.propertyGroup(g).getStringArray(n[i])); }catch(Exception e){} }
  }
  static void sS(Object o,String n,String v)throws Exception{ o.getClass().getMethod("set",String.class,String.class).invoke(o,n,v); }
  static void sA(Object o,String n,String[] v)throws Exception{ o.getClass().getMethod("set",String.class,String[].class).invoke(o,n,v); }
}
