import com.comsol.model.*;
import com.comsol.model.util.*;
import java.util.*;
import java.util.Locale;

/** Step 6e: device delta-neff per volt on the 6d-2 V2 geometry (15-cell supercell, 3 defect cells, 400 nm slab + 1.0 um x 100 nm ridge). */
public class Step6e {
  static final String PZ="D:\\COMSOL63\\Multiphysics\\data\\comsol_piezo_lib.mph";
  static final String BASIC="D:\\COMSOL63\\Multiphysics\\data\\comsol_basic_material_lib.mph";
  static final double P_UM=2.71043685;
  static final int NP=15, ID=7;
  static final int[] DEF={6,7,8};
  static final double WR=1.0e-6, HLN=400e-9, HAL=100e-9, HAIR=2e-6;
  static final double NO=2.211, NEX=2.138, N_AL=1.44, K_AL=16.0, LAM=1.55e-6;
  static final double K0=2*Math.PI/LAM;
  static final double REF_6C2B_NEFF=1.916223, REF_6C2B_DB=0.1043, REF_6B1_W10=1.088174e-4;
  static final double P=P_UM*1e-6, LS=NP*P, XC=(ID+0.5)*P;

  public static void main(String[] args){
    try{
      ModelUtil.initStandalone(true);
      System.out.println("STEP6E_START");
      System.out.println(String.format(Locale.US,"CFG p_um=%.8f NP=%d ID=%d def=%s hLn_nm=400 ridge=1.0um x 100nm air=2um nO=%.3f nE=%.3f nAl=%.2f kAl=%.2f lam_nm=1550",P_UM,NP,ID,Arrays.toString(DEF),NO,NEX,N_AL,K_AL));

      Model m=ModelUtil.create("M6e");
      int[][] G=build(m,100e-9,true);

      String[] o1=optStudy(m,"stdO1",10,"1.916");
      try{
        double[][] dg=evalG(m,o1[1],new String[]{"intLN(real(ewfd.epsilonrxx))/intLN(1)","intLN(real(ewfd.epsilonrzz))/intLN(1)","intAl(real(ewfd.epsilonrxx))/intAl(1)","intAl(imag(ewfd.epsilonrxx))/intAl(1)","(intAll(real(ewfd.epsilonrxx))-intLN(real(ewfd.epsilonrxx))-intAl(real(ewfd.epsilonrxx)))/(intAll(1)-intLN(1)-intAl(1))","ewfd.freq"});
        System.out.println(String.format(Locale.US,"DIAG6E epsLN_xx=%.6f epsLN_zz=%.6f epsAl=(%.4f,%.4f) epsAir=%.6f freq=%.6e",dg[0][0],dg[1][0],dg[2][0],dg[3][0],dg[4][0],dg[5][0]));
      }catch(Throwable t){ System.out.println("DIAG6E_FAIL "+t.getMessage()); }
      double[] te=pickTE0(m,o1[1],"O1");
      if(te==null){ System.out.println("STEP6E_STOP no TE0 found"); return; }
      System.out.println(String.format(Locale.US,"TE0_PICK neff=%.6f neff_im=%.4e dBcm=%.4f TEfrac=%.4f ridgeFrac=%.4f ref6c2b_neff=%.6f ref6c2b_dBcm=%.4f",te[0],te[1],te[2],te[3],te[4],REF_6C2B_NEFF,REF_6C2B_DB));
      String[] o2=optStudy(m,"stdO2",1,String.format(Locale.US,"%.6f",te[0]));
      String SOL=o2[0], DSO=o2[1];
      double[] te2=modeRow(m,DSO,0);
      boolean same=Math.abs(te2[0]-te[0])<1e-6&&te2[3]>0.8;
      System.out.println(String.format(Locale.US,"SOLOPT tag=%s neff=%.8f neff_im=%.4e dBcm=%.4f TEfrac=%.4f ridgeFrac=%.4f same_as_pick=%b",SOL,te2[0],te2[1],te2[2],te2[3],te2[4],same));
      if(!same){ System.out.println("STEP6E_STOP neigs=1 resolve did not return TE0"); return; }
      double Pw=evalG(m,DSO,new String[]{"intAll(ewfd.Poavz)"})[0][0];
      System.out.println(String.format(Locale.US,"POWER P=intAll(withsol('%s',ewfd.Poavz))=%.8e W/m",SOL,Pw));

      defineVars(m,SOL);
      for(String t:m.sol().tags()) try{ m.sol(t).updateSolution(); }catch(Throwable e){ System.out.println("WARN updateSolution "+t+": "+e.getMessage()); }
      String pre=String.format(Locale.US,"epsilon0_const*c_const/(4*(%.12e))*",Pw);

      // self-check (a): uniform index perturbation
      double dTest=evalG(m,DSO,new String[]{pre+"intLN(Wtest)"})[0][0];
      m.param().set("dnL","1e-4");
      String[] o3=optStudy(m,"stdO3",1,String.format(Locale.US,"%.6f",te2[0]));
      double[] te3=modeRow(m,o3[1],0);
      m.param().set("dnL","0");
      double dFD=te3[0]-te2[0];
      double relA=Math.abs(dTest-dFD)/Math.abs(dFD);
      System.out.println(String.format(Locale.US,"SELFCHECK_A dneff_formula=%.6e dneff_FD=%.6e (neff %.8f -> %.8f, TEfrac=%.4f) rel=%.3e ok=%b",dTest,dFD,te2[0],te3[0],te3[3],relA,relA<0.02));
      if(relA>=0.02){ System.out.println("STEP6E_STOP selfcheck A"); return; }

      // self-check (b): ridge top +2 nm
      double dMBt=evalG(m,DSO,new String[]{pre+"intRTop(2[nm]*("+mbH("'"+SOL+"'")+"))"})[0][0];
      Model m2=ModelUtil.create("M6e_r102");
      build(m2,102e-9,false);
      String[] q1=optStudy(m2,"stdO1",10,"1.916");
      double[] tq=pickTE0(m2,q1[1],"R102");
      ModelUtil.remove("M6e_r102");
      double dFDb=tq==null?Double.NaN:tq[0]-te2[0];
      double relB=Math.abs(dMBt-dFDb)/Math.abs(dFDb);
      System.out.println(String.format(Locale.US,"SELFCHECK_B dneff_formula=%.6e dneff_FD=%.6e (neff %.8f -> %.8f) rel=%.3e ok=%b",dMBt,dFDb,te2[0],tq==null?Double.NaN:tq[0],relB,relB<0.05));
      if(!(relB<0.05)){ System.out.println("STEP6E_STOP selfcheck B"); return; }

      // acoustic drive
      String[] a=acStudy(m);
      String DSA=a[1];
      String[] ex={"freq",pre+"intLN(WPE)",pre+"intLN(WEO)",pre+"("+mbAll("'"+SOL+"'")+")"};
      double[][][] r=evalGC(m,DSA,ex);
      double[][] re=r[0], im=r[1];
      int n=re[0].length, ip=0;
      double[] tot=new double[n], fq=new double[n];
      for(int k=0;k<n;k++){
        fq[k]=re[0][k]/1e9;
        double tr=re[1][k]+re[2][k]+re[3][k], ti=im[1][k]+im[2][k]+im[3][k];
        tot[k]=Math.hypot(tr,ti);
        System.out.println(String.format(Locale.US,"F6E f_GHz=%.6f PE=(%.6e,%.6e) EO=(%.6e,%.6e) MB=(%.6e,%.6e) abs_tot=%.6e",
          fq[k],re[1][k],im[1][k],re[2][k],im[2][k],re[3][k],im[3][k],tot[k]));
        if(tot[k]>tot[ip]) ip=k;
      }
      Integer[] ord=new Integer[n]; for(int k=0;k<n;k++) ord[k]=k;
      Arrays.sort(ord,(x,y)->Double.compare(fq[x],fq[y]));
      int jp=0; for(int j=0;j<n;j++) if(ord[j]==ip) jp=j;
      double h=tot[ip]/Math.sqrt(2), lo=Double.NaN, hi=Double.NaN;
      for(int j=jp;j>0;j--){ int a1=ord[j-1], b1=ord[j]; if(tot[a1]<h){ lo=fq[a1]+(h-tot[a1])*(fq[b1]-fq[a1])/(tot[b1]-tot[a1]); break; } }
      for(int j=jp;j<n-1;j++){ int a1=ord[j], b1=ord[j+1]; if(tot[b1]<h){ hi=fq[a1]+(h-tot[a1])*(fq[b1]-fq[a1])/(tot[b1]-tot[a1]); break; } }
      double fw=(hi-lo)*1e3, Q=fq[ip]/(hi-lo);
      double phiL=K0*tot[ip]*1e-3, vpil=LAM/(2*tot[ip])*100;
      System.out.println(String.format(Locale.US,"PEAK6E f_peak_GHz=%.6f abs_tot_peak=%.6e FWHM_MHz=%.4f Q=%.1f phiL_rad_per_mmV=%.4f VpiL_Vcm=%.4f opt_loss_dBcm=%.4f",
        fq[ip],tot[ip],fw,Q,phiL,vpil,te2[2]));
      System.out.println(String.format(Locale.US,"PEAK6E_PARTS PE=(%.6e,%.6e) EO=(%.6e,%.6e) MB=(%.6e,%.6e)",re[1][ip],im[1][ip],re[2][ip],im[2][ip],re[3][ip],im[3][ip]));
      System.out.println(String.format(Locale.US,"COMPARE6B1 TE_window_w1.0=%.6e ratio_6e_over_6b1=%.4f",REF_6B1_W10,tot[ip]/REF_6B1_W10));
      System.out.println("STEP6E_DONE");
    }catch(Throwable t){ System.out.println("STEP6E_ABORT"); t.printStackTrace(System.out); }
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
    m.component("comp1").variable("vPert").set("Wtest",String.format(Locale.US,"%.10e*(abs(Ox)^2+abs(Oy)^2)+%.10e*abs(Oz)^2",2*NO*1e-4,2*NEX*1e-4));
  }
  static String fs(double v){ return String.format(Locale.US,"%.10f",v); }

  static int[][] build(Model m,double hR,boolean acoustic)throws Exception{
    m.param().set("p",String.format(Locale.US,"%.10f[um]",P_UM));
    m.param().set("dnL","0");
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
    System.out.println(String.format(Locale.US,"GEOM6E hR_nm=%.0f nDom=%d nLN=%d(exp 2) nAl=%d(exp %d) nTerm=%d nGnd=%d(exp %d) nTopB=%d nBotB=%d nWallL=%d nWallR=%d nRidgeTop=%d nExt=%d nSideLN=%d",
      hR*1e9,g.getNDomains(),nLN,nAl,nf,G[0].length,G[1].length,nf/2,G[2].length,G[3].length,G[4].length,G[5].length,G[6].length,G[7].length,G[8].length));
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
      m.component("comp1").physics("solid").feature("pzm1").feature("dmp1").set("eta_s","5e-4");
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
    System.out.println(String.format(Locale.US,"NUMELEM6E hR_nm=%.0f acoustic=%b n_elem=%d",hR*1e9,acoustic,m.component("comp1").mesh("mesh1").getNumElem()));
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
        StringBuilder sbp=new StringBuilder("EIGFEAT "+st+" "+ft);
        for(String pn:new String[]{"shift","neigs","transform","eigref","eigwhich"}) try{ sbp.append(" "+pn+"="+m.sol(sol).feature(ft).getString(pn)); }catch(Throwable t){}
        System.out.println(sbp);
        if("outofplanewavenumber".equals(m.sol(sol).feature(ft).getString("transform"))){
          String b=String.format(Locale.US,"%.10e",Double.parseDouble(shift)*K0);
          m.sol(sol).feature(ft).set("shift",b);
          System.out.println("EIGFEAT "+st+" "+ft+" shift_beta="+b);
        }
        m.sol(sol).feature(ft).set("neigs",String.valueOf(neigs));      }catch(Throwable t){ System.out.println("EIGFEAT_WARN "+ft+" "+t.getMessage()); }
    }
    m.study(st).run();
    String ds="ds_"+st;
    m.result().dataset().create(ds,"Solution");
    m.result().dataset(ds).set("solution",sol);
    System.out.println("STUDY "+st+" sol="+sol+" dataset="+ds+" neigs="+neigs+" shift="+shift);
    return new String[]{sol,ds};
  }

  static String[] acStudy(Model m){
    Set<String> sb=new HashSet<>(Arrays.asList(m.sol().tags()));
    TreeSet<Double> fs=new TreeSet<>();
    for(int i=0;i<=40;i++) fs.add(Math.round((3.320+0.001*i)*1e7)/1e7);
    for(int i=0;i<=80;i++) fs.add(Math.round((3.3386+0.00005*i)*1e7)/1e7);
    for(int i=0;i<32;i++) fs.add(Math.round((3.3370+0.00005*i)*1e7)/1e7);
    StringBuilder pl=new StringBuilder();
    for(Double f:fs){ if(pl.length()>0) pl.append(", "); pl.append(String.format(Locale.US,"%.7f[GHz]",f)); }
    m.study().create("stdA");
    m.study("stdA").create("freq","Frequency");
    m.study("stdA").feature("freq").set("plist",pl.toString());
    try{ m.study("stdA").feature("freq").setEntry("activate","ewfd",false); }catch(Throwable t){ System.out.println("WARN deactivate ewfd: "+t.getMessage()); }
    m.study("stdA").createAutoSequences("all");
    String sol=null; for(String t:m.sol().tags()) if(!sb.contains(t)){ sol=t; break; }
    System.out.println("STUDY stdA sol="+sol+" nfreq="+fs.size());
    m.study("stdA").run();
    m.result().dataset().create("ds_stdA","Solution");
    m.result().dataset("ds_stdA").set("solution",sol);
    return new String[]{sol,"ds_stdA"};
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
      System.out.println(String.format(Locale.US,"MODE6E set=%s k=%d neff_re=%.6f neff_im=%.4e dBcm=%.4f TEfrac=%.4f ridgeFrac=%.4f",lab,k,v[0][k],v[1][k],db,te,rf));
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
