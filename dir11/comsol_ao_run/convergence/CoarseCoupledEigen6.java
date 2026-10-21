import com.comsol.model.*; import com.comsol.model.util.*;
public class CoarseCoupledEigen6 {
 public static void main(String[] a)throws Exception{
  ModelUtil.initStandalone(true);Model m=ModelUtil.load("c","D:\\comsol_ao_run\\idt_3d_sus\\aperture_sweep\\Wap_6um\\cli_output_Model.mph");
  try{
   m.component("comp1").selection("selGp").set("condition","inside");m.component("comp1").selection("selGn").set("condition","inside");
   try{m.physics("es").feature().remove("gnd1");}catch(Exception e){}
   try{m.physics("es").feature().remove("ccp1");}catch(Exception e){}
   m.physics("es").create("ccp1","ChargeConservationPiezo",3);m.physics("es").feature("ccp1").selection().named("selLN");
   m.physics("es").create("gndPlus","Ground",2);m.physics("es").feature("gndPlus").selection().named("selGp");
   m.physics("es").create("gndMinus","Ground",2);m.physics("es").feature("gndMinus").selection().named("selGn");
   m.study().create("stdEigCC");m.study("stdEigCC").create("eig","Eigenfrequency");m.study("stdEigCC").feature("eig").set("neigs","12");m.study("stdEigCC").feature("eig").set("shift","3.33[GHz]");m.study("stdEigCC").feature("eig").set("shiftactive","on");m.study("stdEigCC").createAutoSequences("all");
   System.out.println("COARSE_COUPLED_EIG_BEGIN");
   m.study("stdEigCC").run();System.out.println("COARSE_COUPLED_EIG_DONE");
   String[] ds=m.result().dataset().tags();String data=ds[ds.length-1];
   m.result().numerical().create("evEigCC","EvalGlobal");m.result().numerical("evEigCC").set("data",data);m.result().numerical("evEigCC").set("looplevelinput",new String[]{"all"});m.result().numerical("evEigCC").set("expr",new String[]{"freq"});
   double[][] re=m.result().numerical("evEigCC").getReal();
   for(int j=0;j<re[0].length;j++)System.out.printf(java.util.Locale.US,"MODE f_GHz=%.9f%n",re[0][j]/1e9);
   m.result().table().create("tblEigCC","Table");m.result().numerical("evEigCC").set("table","tblEigCC");m.result().numerical("evEigCC").setResult();m.result().table("tblEigCC").save("D:\\comsol_ao_run\\convergence\\Wap_6um_coupled_eigen_coarse.csv");m.save("D:\\comsol_ao_run\\convergence\\Wap_6um_coupled_eigen_coarse.mph");
  }catch(Throwable t){t.printStackTrace(System.out);}finally{ModelUtil.disconnect();}
 }
}
