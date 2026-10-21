import com.comsol.model.*; import com.comsol.model.util.*;
public class DriveAperture6umV3 {
 public static void main(String[] a)throws Exception{
  ModelUtil.initStandalone(true); Model m=ModelUtil.load("d","D:\\comsol_ao_run\\convergence\\Wap_6um_fine_Model.mph");
  try{
   m.component("comp1").selection("selGp").set("condition","inside");
   m.component("comp1").selection("selGn").set("condition","inside");
   try{m.physics("es").feature().remove("gnd1");}catch(Exception e){}
   m.physics("es").create("termDrive","Terminal",2);m.physics("es").feature("termDrive").selection().named("selGp");m.physics("es").feature("termDrive").set("TerminalType","Voltage");m.physics("es").feature("termDrive").set("V0","1[V]");
   m.physics("es").create("gndDrive","Ground",2);m.physics("es").feature("gndDrive").selection().named("selGn");
   try{m.physics("es").feature().remove("ccp1");}catch(Exception e){}
   m.physics("es").create("ccp1","ChargeConservationPiezo",3);m.physics("es").feature("ccp1").selection().named("selLN");
   m.physics("solid").feature("pzm1").create("dmpDrive","Damping",3);m.physics("solid").feature("pzm1").feature("dmpDrive").set("DampingType","IsotropicLossFactor");m.physics("solid").feature("pzm1").feature("dmpDrive").set("eta_s_mat","userdef");m.physics("solid").feature("pzm1").feature("dmpDrive").set("eta_s","5e-4");
   m.study().create("stdDrive3");m.study("stdDrive3").create("freq","Frequency");m.study("stdDrive3").feature("freq").set("plist","3.3044e9[Hz]");m.study("stdDrive3").createAutoSequences("all");
   System.out.println("BOUNDARIES gp="+java.util.Arrays.toString(m.component("comp1").selection("selGp").entities())+" gn="+java.util.Arrays.toString(m.component("comp1").selection("selGn").entities()));
   System.out.println("CCP="+java.util.Arrays.toString(m.physics("es").feature("ccp1").selection().entities()));
   m.study("stdDrive3").run(); System.out.println("SOLVE_DONE");
   String[] ds=m.result().dataset().tags();String data=ds[ds.length-1];
   m.result().numerical().create("evDrive3","EvalGlobal");m.result().numerical("evDrive3").set("data",data);
   m.result().numerical("evDrive3").set("expr",new String[]{"freq","intLN(abs(V))","intLN(abs(u))","intLN(abs(v))","intLN(abs(w))","intLN(abs(solid.eXX))","intLN(abs(solid.eYY))","intLN(abs(solid.eZZ))","intLN(1)"});
   double[][] re=m.result().numerical("evDrive3").getReal();
   for(int j=0;j<re[0].length;j++)System.out.printf(java.util.Locale.US,"ROW f_GHz=%.9f V_int=%.6e u_int=%.6e v_int=%.6e w_int=%.6e eXX_int=%.6e eYY_int=%.6e eZZ_int=%.6e LNvol=%.6e%n",re[0][j]/1e9,re[1][j],re[2][j],re[3][j],re[4][j],re[5][j],re[6][j],re[7][j],re[8][j]);
   m.result().table().create("tblDrive3","Table");m.result().numerical("evDrive3").set("table","tblDrive3");m.result().numerical("evDrive3").setResult();m.result().table("tblDrive3").save("D:\\comsol_ao_run\\convergence\\Wap_6um_fine_driven_1V_ccp.csv");
   m.save("D:\\comsol_ao_run\\convergence\\Wap_6um_fine_driven_Model_ccp.mph");
  }catch(Throwable t){t.printStackTrace(System.out);}finally{ModelUtil.disconnect();}
 }
}
