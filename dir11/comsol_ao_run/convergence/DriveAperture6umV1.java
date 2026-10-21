import com.comsol.model.*; import com.comsol.model.util.*;
public class DriveAperture6umV1 {
 public static void main(String[] args)throws Exception{
  ModelUtil.initStandalone(true); Model m=ModelUtil.load("d","D:\\comsol_ao_run\\convergence\\Wap_6um_fine_Model.mph");
  try{
   try{m.physics("es").feature().remove("gnd1");}catch(Exception e){}
   m.physics("es").create("termDrive","Terminal",2);m.physics("es").feature("termDrive").selection().named("selGp");m.physics("es").feature("termDrive").set("TerminalType","Voltage");m.physics("es").feature("termDrive").set("V0","1");
   m.physics("es").create("gndDrive","Ground",2);m.physics("es").feature("gndDrive").selection().named("selGn");
   m.physics("solid").feature("pzm1").create("dmpDrive","Damping",3);m.physics("solid").feature("pzm1").feature("dmpDrive").set("DampingType","IsotropicLossFactor");m.physics("solid").feature("pzm1").feature("dmpDrive").set("eta_s_mat","userdef");m.physics("solid").feature("pzm1").feature("dmpDrive").set("eta_s","5e-4");
   m.multiphysics().remove("pze1");m.multiphysics().create("pze1","PiezoelectricEffect","geom1");
   m.study().create("stdDrive");m.study("stdDrive").create("freq","Frequency");m.study("stdDrive").feature("freq").set("plist","3.291194e9[Hz]");m.study("stdDrive").createAutoSequences("all");m.study("stdDrive").run();
   String[] ds=m.result().dataset().tags();String data=ds[ds.length-1];System.out.println("DATA="+data+" TERMINAL="+java.util.Arrays.toString(m.physics("es").feature("termDrive").selection().entities())+" GROUND="+java.util.Arrays.toString(m.physics("es").feature("gndDrive").selection().entities())+" V0="+m.physics("es").feature("termDrive").getString("V0"));
   m.result().numerical().create("ev","EvalGlobal");m.result().numerical("ev").set("data",data);m.result().numerical("ev").set("expr",new String[]{"freq","intLN(abs(V))","intLN(abs(u))","intLN(abs(v))","intLN(abs(w))","intLN(abs(solid.eXX))","intLN(abs(solid.eYY))","intLN(abs(solid.eZZ))"});double[][] r=m.result().numerical("ev").getReal();for(int i=0;i<r.length;i++)System.out.println("ROW"+i+"="+r[i][0]);
   m.save("D:\\comsol_ao_run\\convergence\\Wap_6um_fine_driven_testV1.mph");
  }catch(Throwable t){t.printStackTrace(System.out);}finally{ModelUtil.disconnect();}
 }
}



