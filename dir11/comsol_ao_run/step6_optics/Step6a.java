import com.comsol.model.*;
import com.comsol.model.util.*;
import java.lang.reflect.*;
import java.util.*;
import java.util.Locale;

/** Step 6a: Step5 drive model, sweep 133 pts, light path B avg/K + binned dn(x) at 2 freqs. */
public class Step6a {
  static final String PZ="D:\\COMSOL63\\Multiphysics\\data\\comsol_piezo_lib.mph";
  static final String BASIC="D:\\COMSOL63\\Multiphysics\\data\\comsol_basic_material_lib.mph";
  static final double P_UM=2.8526131500, LAM=1550e-9;
  static final double NE=2.138, NEFFB=1.88978, KB=4.052926e6;
  static final int NBIN=114;
  static final double DX=(P_UM*1e-6)/NBIN;

  public static void main(String[] args){
    try{
      ModelUtil.initStandalone(true);
      System.out.println("STEP6A_START");
      System.out.println(String.format(Locale.US,"SELFCHECK phiL=%.6f expect=0.4054",(2*Math.PI/LAM)*1e-4*1e-3));
      Model m=ModelUtil.create("M6a");
      build(m);
      TreeSet<Double> fs=new TreeSet<Double>();
      for(int i=0;i<=50;i++) fs.add(3.31+0.001*i);
      for(int i=0;i<=80;i++) fs.add(3.3280+0.00005*i);
      fs.add(3.20); fs.add(3.45);
      double[] fl=new double[fs.size()]; int k=0; for(Double x:fs) fl[k++]=x;
      System.out.println("NFREQ "+fl.length+" DX_um="+String.format(Locale.US,"%.8f",DX*1e6));
      StringBuilder pl=new StringBuilder(); for(Double x:fs){ if(pl.length()>0) pl.append(", "); pl.append(String.format(Locale.US,"%.9f[GHz]",x)); }
      m.study().create("stdF"); m.study("stdF").create("freq","Frequency"); m.study("stdF").feature("freq").set("plist",pl.toString()); m.study("stdF").createAutoSequences("all");
      m.study("stdF").run();
      String ds=last(m); System.out.println("DATASET "+ds);
      checkTensor(m,ds);
      // base + B avg/K
      double p=P_UM*1e-6; double hLn=500e-9; double eTop=Math.cos(KB*hLn/2); double et2=eTop*eTop;
      double NB=coreN(); double cPE=NE/(NEFFB*NB); double cMB=(NE*NE-1)*et2/(2*NEFFB*NB);
      List<String> ex=new ArrayList<String>();
      ex.add("freq"); ex.add("i*2*pi*freq*(es.Q0_1)"); ex.add("intLN(abs(u)^2+abs(v)^2+abs(w)^2)"); ex.add("mx(abs(v))");
      for(int j=0;j<3;j++){ String d=(j==0?"dnB":(j==1?"eoB":"MBX")); for(int n=0;n<2;n++) ex.add(avgExpr(d,n)); }
      m.result().numerical().create("g0","EvalGlobal"); m.result().numerical("g0").set("data",ds);
      m.result().numerical("g0").set("expr",ex.toArray(new String[0])); m.result().numerical("g0").set("looplevelinput",new String[]{"all"});
      double[][] re0=m.result().numerical("g0").getReal(); double[][] im0=m.result().numerical("g0").getImag();
      int nf=re0[0].length;
      // find peak index in fine scan 3.328-3.332
      int ip=0; double best=-1;
      for(int i=0;i<nf;i++){ double f=re0[0][i]/1e9; if(f>=3.328&&f<=3.332){ double y=Math.hypot(re0[1][i],im0[1][i]); if(y>best){best=y;ip=i;} } }
      int i320=0; double bd=9; for(int i=0;i<nf;i++){ double d=Math.abs(re0[0][i]/1e9-3.20); if(d<bd){bd=d;i320=i;} }
      System.out.println("PEAK_INDEX "+ip+" PEAK_F_GHz="+String.format(Locale.US,"%.9f",re0[0][ip]/1e9)+" PEAK_ABS_Y="+String.format(Locale.US,"%.9e",best));
      System.out.println("REF320_INDEX "+i320+" F="+String.format(Locale.US,"%.9f",re0[0][i320]/1e9));
      // print sweep lines with B avg/K
      for(int i=0;i<nf;i++){
        StringBuilder sb=new StringBuilder();
        sb.append(String.format(Locale.US,"SWA6 f_GHz=%.9f ReY=%.9e ImY=%.9e int_u2=%.9e max_v=%.9e",re0[0][i]/1e9,re0[1][i],im0[1][i],re0[2][i],re0[3][i]));
        for(int j=0;j<3;j++){
          int b=4+j*2; double[] av={re0[b][i],im0[b][i]}; double[] kk={re0[b+1][i],im0[b+1][i]};
          String nm=j==0?"PE":(j==1?"EO":"MB");
          sb.append(String.format(Locale.US," %s_avgRe=%.6e %s_avgIm=%.6e %s_avgAbs=%.6e %s_KRe=%.6e %s_KIm=%.6e %s_KAbs=%.6e",nm,av[0],nm,av[1],nm,Math.hypot(av[0],av[1]),nm,kk[0],nm,kk[1],nm,Math.hypot(kk[0],kk[1])));
        }
        System.out.println(sb.toString());
      }
      // scale factors for B metrics
      double[] scale={cPE,cPE,cMB};
      double[][][] q=new double[3][2][2];
      for(int i=0;i<nf;i++){ /* nothing */ }
      // bins at ip and i320
      List<String> bx=new ArrayList<String>(); bx.add("freq"); bx.add("(1/p)*intLN(dnB*Eopt2)"); bx.add("(2/p)*intLN(dnB*Eopt2*exp(-i*2*pi*x/p))"); bx.add("(1/p)*intLN(eoB*Eopt2)"); bx.add("(2/p)*intLN(eoB*Eopt2*exp(-i*2*pi*x/p))"); bx.add("(1/p)*(intTop(v)-intBot(v))"); bx.add("(2/p)*(intTop(v*exp(-i*2*pi*x/p))-intBot(v*exp(-i*2*pi*x/p)))");
      for(int j=0;j<NBIN;j++){ double a=j*DX, b=a+DX; String ind="(x>="+j+"*p/114)*(x<"+(j+1)+"*p/114)"; bx.add("intLN(dnB*Eopt2*"+ind+")"); }
      for(int j=0;j<NBIN;j++){ double a=j*DX, b=a+DX; String ind="(x>="+j+"*p/114)*(x<"+(j+1)+"*p/114)"; bx.add("intLN(eoB*Eopt2*"+ind+")"); }
      for(int j=0;j<NBIN;j++){ double a=j*DX, b=a+DX; String ind="(x>="+j+"*p/114)*(x<"+(j+1)+"*p/114)"; bx.add("(intTop(v*"+ind+")-intBot(v*"+ind+"))"); }
      for(int pick=0;pick<2;pick++){
        int idx=pick==0?ip:i320; double fr=re0[0][idx]/1e9;
        String tag="gb"+pick;
        m.result().numerical().create(tag,"EvalGlobal"); m.result().numerical(tag).set("data",ds);
        m.result().numerical(tag).set("expr",bx.toArray(new String[0])); m.result().numerical(tag).set("looplevelinput",new String[]{"manual"});
        m.result().numerical(tag).set("looplevel",new int[]{idx+1});
        double[][] r=m.result().numerical(tag).getReal(); double[][] im=m.result().numerical(tag).getImag();
        double[] dnPE=new double[NBIN], dnEO=new double[NBIN], dnMB=new double[NBIN];
        for(int j=0;j<NBIN;j++){ dnPE[j]=r[7+j][0]*cPE/DX; dnEO[j]=r[7+NBIN+j][0]*cPE/DX; dnMB[j]=r[7+2*NBIN+j][0]*cMB/DX; }
        double[] imPE=new double[NBIN],imEO=new double[NBIN],imMB=new double[NBIN];
        for(int j=0;j<NBIN;j++){ imPE[j]=im[7+j][0]*cPE/DX; imEO[j]=im[7+NBIN+j][0]*cPE/DX; imMB[j]=im[7+2*NBIN+j][0]*cMB/DX; }
        // self-check vs q0/q1
        double[] avPE={r[1][0]*cPE,im[1][0]*cPE}, kPE={r[2][0]*cPE,im[2][0]*cPE};
        double[] avEO={r[3][0]*cPE,im[3][0]*cPE}, kEO={r[4][0]*cPE,im[4][0]*cPE};
        double[] avMB={r[5][0]*cMB,im[5][0]*cMB}, kMB={r[6][0]*cMB,im[6][0]*cMB};
        double[] sumPE={0,0},sumEO={0,0},sumMB={0,0},sumKPE={0,0},sumKEO={0,0},sumKMB={0,0};
        for(int j=0;j<NBIN;j++){ double xc=(j+0.5)*DX; double th=2*Math.PI*xc/p; double c=Math.cos(th), s=-Math.sin(th);
          sumPE[0]+=dnPE[j]*DX/p; sumPE[1]+=imPE[j]*DX/p;
          sumEO[0]+=dnEO[j]*DX/p; sumEO[1]+=imEO[j]*DX/p;
          sumMB[0]+=dnMB[j]*DX/p; sumMB[1]+=imMB[j]*DX/p;
          sumKPE[0]+=(dnPE[j]*c-imPE[j]*s)*DX*2/p; sumKPE[1]+=(dnPE[j]*s+imPE[j]*c)*DX*2/p;
          sumKEO[0]+=(dnEO[j]*c-imEO[j]*s)*DX*2/p; sumKEO[1]+=(dnEO[j]*s+imEO[j]*c)*DX*2/p;
          sumKMB[0]+=(dnMB[j]*c-imMB[j]*s)*DX*2/p; sumKMB[1]+=(dnMB[j]*s+imMB[j]*c)*DX*2/p;
        }
        double[] qPE=avPE,qKPE=kPE;
        double[] qEO=avEO,qKEO=kEO;
        double[] qMB=avMB,qKMB=kMB;
        System.out.println(String.format(Locale.US,"BIN_FREQ f_bin_GHz=%.9f refRep_Re=%.6e refRep_Im=%.6e refK_Re=%.6e refK_Im=%.6e x_first=0 last=p",r[0][0]/1e9,sumPE[0],sumPE[1],sumKPE[0],sumKPE[1]));
        System.out.println(String.format(Locale.US,"BIN_REF f_GHz=%.9f sumAvgPE=(%.6e,%.6e) refAvgPE=(%.6e,%.6e) sumAvgEO=(%.6e,%.6e) refAvgEO=(%.6e,%.6e) sumAvgMB=(%.6e,%.6e) refAvgMB=(%.6e,%.6e)",r[0][0]/1e9,sumPE[0],sumPE[1],avPE[0],avPE[1],sumEO[0],sumEO[1],avEO[0],avEO[1],sumMB[0],sumMB[1],avMB[0],avMB[1]));
        System.out.println(String.format(Locale.US,"BINCHECK f_GHz=%.9f avgPE_rel=%.4e avgEO_rel=%.4e avgMB_rel=%.4e KPE_rel=%.4e KEO_rel=%.4e KMB_rel=%.4e",
          fr,rel(sumPE,qPE),rel(sumEO,qEO),rel(sumMB,qMB),rel(sumKPE,qKPE),rel(sumKEO,qKEO),rel(sumKMB,qKMB)));
        for(int j=0;j<NBIN;j++) System.out.println(String.format(Locale.US,"BIN6 f_GHz=%.9f j=%d xc_um=%.6f PE_Re=%.6e PE_Im=%.6e EO_Re=%.6e EO_Im=%.6e MB_Re=%.6e MB_Im=%.6e",
          fr,j,(j+0.5)*DX*1e6,dnPE[j],imPE[j],dnEO[j],imEO[j],dnMB[j],imMB[j]));
        // windows from bins
        for(int wi=0;wi<3;wi++){ int mm=(int)Math.round((wi==0?0.3:(wi==1?0.5:0.8))*1e-6/DX); int bestj=0; double bestA=-1; double[] bestV={0,0};
          for(int j0=0;j0<NBIN;j0++){ double sre=0,sim=0; for(int q2=0;q2<mm;q2++){ int jj=(j0+q2)%NBIN; sre+=dnPE[jj]+dnEO[jj]+dnMB[jj]; sim+=imPE[jj]+imEO[jj]+imMB[jj]; } sre/=mm; sim/=mm; double a=Math.hypot(sre,sim); if(a>bestA){bestA=a;bestj=j0;bestV=new double[]{sre,sim};} }
          System.out.println(String.format(Locale.US,"WIN6 f_GHz=%.9f w_um=%.2f j0=%d x0_um=%.6f Tot_Re=%.6e Tot_Im=%.6e Tot_Abs=%.6e",fr,wi==0?0.3:(wi==1?0.5:0.8),bestj,bestj*DX*1e6,bestV[0],bestV[1],bestA));
        }
      }
      // point check at peak
      pointCheck(m,ds,ip);
      // antiresonance & k2
      double fr=re0[0][ip]/1e9; double fa=0; double minY=1e18;
      for(int i=0;i<nf;i++){ double f=re0[0][i]/1e9; if(f>=3.31&&f<=3.36){ double y=Math.hypot(re0[1][i],im0[1][i]); if(y<minY){minY=y;fa=f;} } }
      System.out.println(String.format(Locale.US,"RES6 fr_GHz=%.9f Yr=%.9e fa_GHz=%.9f Ya=%.9e k2=%.6e",fr,best,fa,minY,(fa*fa-fr*fr)/(fa*fa)));
      ModelUtil.remove("M6a");
      System.out.println("STEP6A_DONE");
    }catch(Throwable t){ System.out.println("STEP6A_ABORT"); t.printStackTrace(System.out); }
  }
  static String last(Model m){ String[] d=m.result().dataset().tags(); return d[d.length-1]; }
  static double rel(double[] a,double[] b){ double n=Math.hypot(b[0],b[1]); if(n<1e-30) return 0; return Math.hypot(a[0]-b[0],a[1]-b[1])/n; }
  static String fmt(double v){ return String.format(Locale.US,"%.10e",v); }
  static String avgExpr(String d,int n){ double p=P_UM*1e-6; if(d.equals("MBX")) return n==0? "("+fmt(1/p)+")*(intTop(v)-intBot(v))" : "("+fmt(2/p)+")*(intTop(v*exp(-i*2*pi*x/p))-intBot(v*exp(-i*2*pi*x/p)))"; return n==0? "("+fmt(1/p)+")*intLN("+d+"*Eopt2)" : "("+fmt(2/p)+")*intLN("+d+"*Eopt2*exp(-i*2*pi*x/p))"; }
  static double coreN(){ double h=500e-9; double core=h/2+Math.sin(KB*h)/(2*KB); double gam=Math.sqrt(NEFFB*NEFFB-1)*2*Math.PI/LAM; double e=Math.cos(KB*h/2); return core+e*e/gam; }
  static void copyGroup(Material d,Material s,String g,boolean c){ if(c)d.propertyGroup().create(g,g); String[] n=s.propertyGroup(g).properties(); for(int i=0;i<n.length;i++){ try{ d.propertyGroup(g).set(n[i],s.propertyGroup(g).getStringArray(n[i])); }catch(Exception e){} } }
  static void box(Model m,String t,int dim,String x0,String x1,String y0,String y1,String cond){ m.component("comp1").selection().create(t,"Box"); m.component("comp1").selection(t).set("entitydim",""+dim); m.component("comp1").selection(t).set("condition",cond); m.component("comp1").selection(t).set("xmin",x0); m.component("comp1").selection(t).set("xmax",x1); m.component("comp1").selection(t).set("ymin",y0); m.component("comp1").selection(t).set("ymax",y1); }
  static String gS(Object o,String n){ try{ return (String)o.getClass().getMethod("getString",String.class).invoke(o,n);}catch(Throwable t){return "ERR";} }
  static void sS(Object o,String n,String v)throws Exception{ o.getClass().getMethod("set",String.class,String.class).invoke(o,n,v); }
  static void sA(Object o,String n,String[] v)throws Exception{ o.getClass().getMethod("set",String.class,String[].class).invoke(o,n,v); }
  static int[] sideE(Model m,boolean ln){ int nE=m.geom("geom1").getNEdges(); int[] L=new int[nE],R=new int[nE]; int nl=0,nr=0; double pm=0; for(int e=1;e<=nE;e++){double[][] a=m.geom("geom1").edgeX(e,new double[]{0.5}); pm=Math.max(pm,a[0][0]);} for(int e=1;e<=nE;e++){double[][] a=m.geom("geom1").edgeX(e,new double[]{0.02,0.98}); double x0=a[0][0],y0=a[0][1],x1=a[1][0],y1=a[1][1]; if(Math.abs(x0-x1)>1e-10||Math.abs(y0-y1)<1e-10)continue; double yl=Math.min(y0,y1),yh=Math.max(y0,y1); if(ln&&(yl<-1e-9||yh>500e-9+1e-9))continue; if(Math.abs(x0)<1e-9)L[nl++]=e; if(Math.abs(x0-pm)<1e-9)R[nr++]=e;} int[] u=new int[nl+nr]; System.arraycopy(L,0,u,0,nl); System.arraycopy(R,0,u,nl,nr); return u; }
  static void applyPer(Model m){ m.physics("solid").feature("pc1").selection().set(sideE(m,false)); m.physics("es").feature("pc1").selection().set(sideE(m,true)); }
  static void checkTensor(Model m,String ds){ try{ m.result().numerical().create("gt","EvalGlobal"); m.result().numerical("gt").set("data",ds); m.result().numerical("gt").set("expr",new String[]{"intLN(solid.cEg22)/intLN(1)","intLN(solid.cEg33)/intLN(1)","intLN(solid.cEg15)/intLN(1)","intLN(solid.cEg25)/intLN(1)","intLN(solid.cEg46)/intLN(1)"}); double[][] r=m.result().numerical("gt").getReal(); for(int i=0;i<5;i++) System.out.println(String.format(Locale.US,"TENSOR_CHECK i=%d value=%.8e",i,r[i][0])); }catch(Throwable t){ System.out.println("TENSOR_NA "+t.getMessage()); } }
  static void pointCheck(Model m,String ds,int idx){ try{ m.result().dataset().create("cpt","CutPoint2D"); m.result().dataset("cpt").set("pointx","p/2"); m.result().dataset("cpt").set("pointy","hLn/2"); m.result().numerical().create("pe","EvalPoint"); m.result().numerical("pe").set("data","cpt"); m.result().numerical("pe").set("expr",new String[]{"es.Ex","es.Ey","solid.eXX","solid.eYY","v"}); m.result().numerical("pe").set("looplevelinput",new String[]{"manual"}); m.result().numerical("pe").set("looplevel",new int[]{idx+1}); double[][] r=m.result().numerical("pe").getReal(); double[][] im=m.result().numerical("pe").getImag(); System.out.println(String.format(Locale.US,"POINT6 Ex=%.6e/%.6e Ey=%.6e/%.6e exx=%.6e/%.6e eyy=%.6e/%.6e v=%.6e/%.6e",r[0][0],im[0][0],r[1][0],im[1][0],r[2][0],im[2][0],r[3][0],im[3][0],r[4][0],im[4][0])); }catch(Throwable t){ System.out.println("POINT6_NA "+t.getMessage()); } }
  static void build(Model m)throws Exception{
    m.param().set("p",String.format(Locale.US,"%.10f[um]",P_UM)); m.param().set("hLn","500[nm]"); m.param().set("hAl","100[nm]"); m.param().set("duty","0.25");
    m.modelNode().create("comp1"); m.geom().create("geom1",2); m.geom("geom1").lengthUnit("m");
    feat(m,"rLn","Rectangle",new String[]{"p","hLn"},new String[]{"0","0"});
    feat(m,"rAp","Rectangle",new String[]{"duty*p","hAl"},new String[]{"(p-2*duty*p)/4","hLn"});
    feat(m,"rAn","Rectangle",new String[]{"duty*p","hAl"},new String[]{"p/2+(p-2*duty*p)/4","hLn"});
    m.geom("geom1").run();
    box(m,"selLN",2,"1[nm]","p-1[nm]","1[nm]","hLn-1[nm]","intersects");
    box(m,"selAl",2,"1[nm]","p-1[nm]","hLn+1[nm]","hLn+hAl-1[nm]","intersects");
    box(m,"selTerm",1,"(p-2*duty*p)/4-1[nm]","(p-2*duty*p)/4+duty*p+1[nm]","hLn-1[nm]","hLn+1[nm]","inside");
    box(m,"selGn",1,"p/2+(p-2*duty*p)/4-1[nm]","p/2+(p-2*duty*p)/4+duty*p+1[nm]","hLn-1[nm]","hLn+1[nm]","inside");
    box(m,"selTop",1,"-1[nm]","p+1[nm]","hLn-1[nm]","hLn+1[nm]","inside");
    box(m,"selBot",1,"-1[nm]","p+1[nm]","-1[nm]","1[nm]","inside");
    System.out.println("GROUND_CHECK nTerm="+m.component("comp1").selection("selTerm").entities().length+" nGn="+m.component("comp1").selection("selGn").entities().length);
    Model pz=ModelUtil.load("pz",PZ); Model bs=ModelUtil.load("basic",BASIC);
    Material ln=m.component("comp1").material().create("matLN","Common"); ln.selection().named("selLN");
    copyGroup(ln,pz.material("lithium_niobate"),"def",false); copyGroup(ln,pz.material("lithium_niobate"),"StressCharge",true);
    Material al=m.component("comp1").material().create("matAl","Common"); al.selection().named("selAl");
    copyGroup(al,bs.material("aluminum"),"def",false); copyGroup(al,bs.material("aluminum"),"Enu",true);
    ModelUtil.remove("pz"); ModelUtil.remove("bs");
    m.component("comp1").variable().create("vO"); m.component("comp1").variable("vO").selection().named("selLN");
    m.component("comp1").variable("vO").set("Eopt2","cos("+String.format(Locale.US,"%.9e",KB)+"[1/m]*(y-hLn/2))^2");
    m.component("comp1").variable("vO").set("dnB","-("+String.format(Locale.US,"%.6f",Math.pow(NE,3)/2)+")*(0.179*(solid.eYY+solid.eXX)+0.071*solid.eZZ)");
    m.component("comp1").variable("vO").set("eoB","-("+String.format(Locale.US,"%.6f",Math.pow(NE,3)/2)+")*(8.6e-12[m/V]*(es.Ey-es.Ex)+30.8e-12[m/V]*es.Ez)");
    m.physics().create("solid","SolidMechanics","geom1"); m.physics().create("es","Electrostatics","geom1"); m.physics("es").selection().named("selLN");
    m.physics("solid").create("pzm1","PiezoelectricMaterialModel",2); m.physics("solid").feature("pzm1").selection().named("selLN");
    m.multiphysics().create("pze1","PiezoelectricEffect","geom1");
    m.physics("es").create("ccp1","ChargeConservationPiezo",2); m.physics("es").feature("ccp1").selection().named("selLN");
    Object sys=m.component("comp1").coordSystem().create("sys2","Rotated"); sS(sys,"rotationSequence","ZXZ"); sA(sys,"angle",new String[]{"90[deg]","0","0"});
    sS(m.physics("solid").feature("pzm1"),"coordinateSystem","sys2"); sS(m.physics("es").feature("ccp1"),"coordinateSystem","sys2");
    m.physics("solid").feature("pzm1").create("dmp1","Damping",2); m.physics("solid").feature("pzm1").feature("dmp1").set("DampingType","IsotropicLossFactor"); m.physics("solid").feature("pzm1").feature("dmp1").set("eta_s_mat","userdef"); m.physics("solid").feature("pzm1").feature("dmp1").set("eta_s","5e-4");
    m.physics("es").create("term1","Terminal",1); m.physics("es").feature("term1").selection().named("selTerm"); m.physics("es").feature("term1").set("TerminalType","Voltage"); m.physics("es").feature("term1").set("V0","1[V]");
    m.physics("es").create("gnd1","Ground",1); m.physics("es").feature("gnd1").selection().named("selGn");
    System.out.println("TERMINAL_CHECK nTerm="+m.component("comp1").selection("selTerm").entities().length+" nGnd="+m.component("comp1").selection("selGn").entities().length);
    m.physics("solid").create("pc1","PeriodicCondition",1); m.physics("es").create("pc1","PeriodicCondition",1); applyPer(m);
    Object pr=m.physics("solid").prop("Type2D"); sS(pr,"ModeExtension","1"); sS(pr,"kz","0");
    m.component("comp1").cpl().create("intLN","Integration"); m.component("comp1").cpl("intLN").selection().geom("geom1",2); m.component("comp1").cpl("intLN").selection().named("selLN");
    m.component("comp1").cpl().create("intTop","Integration"); m.component("comp1").cpl("intTop").selection().geom("geom1",1); m.component("comp1").cpl("intTop").selection().named("selTop");
    m.component("comp1").cpl().create("intBot","Integration"); m.component("comp1").cpl("intBot").selection().geom("geom1",1); m.component("comp1").cpl("intBot").selection().named("selBot");
    m.component("comp1").cpl().create("mx","Maximum"); m.component("comp1").cpl("mx").selection().geom("geom1",2); m.component("comp1").cpl("mx").selection().named("selLN");
    m.mesh().create("mesh1","geom1");
    m.mesh("mesh1").feature().create("szLN","Size"); m.mesh("mesh1").feature("szLN").selection().geom("geom1",2); m.mesh("mesh1").feature("szLN").selection().named("selLN"); m.mesh("mesh1").feature("szLN").set("hmaxactive","on"); m.mesh("mesh1").feature("szLN").set("hmax","40[nm]");
    m.mesh("mesh1").feature().create("ftri1","FreeTri"); m.mesh("mesh1").feature("ftri1").selection().geom("geom1",2); m.mesh("mesh1").feature("ftri1").selection().all(); m.mesh("mesh1").run();
    System.out.println("NUMELEM n_elem="+m.mesh("mesh1").getNumElem());
  }
  static void feat(Model m,String t,String type,String[] sz,String[] pos){ m.geom("geom1").feature().create(t,type); m.geom("geom1").feature(t).set("size",sz); m.geom("geom1").feature(t).set("pos",pos); }
}
