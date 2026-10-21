import com.comsol.model.*; import com.comsol.model.util.*;
public class DriveAperture6umV2 {
 public static void main(String[] a)throws Exception{
  ModelUtil.initStandalone(true);
  Model m=ModelUtil.load("d","D:\\comsol_ao_run\\convergence\\Wap_6um_fine_Model.mph");
  try{
   m.component("comp1").selection("selGp").set("condition","inside");
   m.component("comp1").selection("selGn").set("condition","inside");
   int[] gp=m.component("comp1").selection("selGp").entities(), gn=m.component("comp1").selection("selGn").entities();
   System.out.println("DRIVE_BNDS gp="+java.util.Arrays.toString(gp)+" gn="+java.util.Arrays.toString(gn));
   try{m.physics("es").feature().remove("gnd1");}catch(Exception e){}
   m.physics("es").create("termDrive","Terminal",2);
   m.physics("es").feature("termDrive").selection().named("selGp");
   m.physics("es").feature("termDrive").set("TerminalType","Voltage");
   m.physics("es").feature("termDrive").set("V0","1[V]");
   m.physics("es").create("gndDrive","Ground",2);
   m.physics("es").feature("gndDrive").selection().named("selGn");
   m.physics("solid").feature("pzm1").create("dmpDrive","Damping",3);
   m.physics("solid").feature("pzm1").feature("dmpDrive").set("DampingType","IsotropicLossFactor");
   m.physics("solid").feature("pzm1").feature("dmpDrive").set("eta_s_mat","userdef");
   m.physics("solid").feature("pzm1").feature("dmpDrive").set("eta_s","5e-4");
   m.study().create("stdDrive2");
   m.study("stdDrive2").create("freq","Frequency");
   m.study("stdDrive2").feature("freq").set("plist","3.302e9[Hz] 3.3034e9[Hz] 3.3040e9[Hz] 3.3044e9[Hz] 3.3048e9[Hz] 3.3054e9[Hz] 3.3068e9[Hz]");
   m.study("stdDrive2").createAutoSequences("all");
   System.out.println("DRIVE_SOLVE_START");
   m.study("stdDrive2").run();
   System.out.println("DRIVE_SOLVE_DONE");
   String[] ds=m.result().dataset().tags(); String data=ds[ds.length-1];
   m.result().numerical().create("evDrive2","EvalGlobal"); m.result().numerical("evDrive2").set("data",data);
   m.result().numerical("evDrive2").set("looplevelinput",new String[]{"all"});
   m.result().numerical("evDrive2").set("expr",new String[]{"freq","intLN(abs(V))","intLN(abs(u))","intLN(abs(v))","intLN(abs(w))","maxLN(sqrt(u^2+v^2+w^2))","maxLN(abs(solid.eXX))","maxLN(abs(solid.eYY))","maxLN(abs(solid.eZZ))","maxLN(abs(V))"});
   double[][] re=m.result().numerical("evDrive2").getReal();
   for(int j=0;j<re[0].length;j++) System.out.printf(java.util.Locale.US,"ROW f_GHz=%.9f V_int=%.6e u_int=%.6e v_int=%.6e w_int=%.6e umax_nm=%.6e eXXmax=%.6e eYYmax=%.6e eZZmax=%.6e Vmax=%.6e%n",re[0][j]/1e9,re[1][j],re[2][j],re[3][j],re[4][j],re[5][j]*1e9,re[6][j],re[7][j],re[8][j],re[9][j]);
   m.result().table().create("tblDrive2","Table");m.result().numerical("evDrive2").set("table","tblDrive2");m.result().numerical("evDrive2").setResult();
   m.result().table("tblDrive2").save("D:\\comsol_ao_run\\convergence\\Wap_6um_fine_driven_1V_corrected.csv");
   m.save("D:\\comsol_ao_run\\convergence\\Wap_6um_fine_driven_Model_corrected.mph");
  }catch(Throwable t){t.printStackTrace(System.out);}finally{ModelUtil.disconnect();}
 }
}
