import com.comsol.model.*; import com.comsol.model.util.*;
public class DriveCoupledEigen {
 public static void main(String[] a)throws Exception{
  ModelUtil.initStandalone(true);Model m=ModelUtil.load("d","D:\\comsol_ao_run\\convergence\\DriveAperture6umV3_d.mph");
  try{
   try{m.physics("es").feature().remove("termDrive");}catch(Exception e){}
   try{m.physics("es").feature().remove("ccp1");}catch(Exception e){}
   m.physics("es").create("ccpCoupled","ChargeConservationPiezo",3);m.physics("es").feature("ccpCoupled").selection().named("selLN");
   m.physics("es").create("gndPlus","Ground",2);m.physics("es").feature("gndPlus").selection().named("selGp");
   try{m.physics("solid").feature("pzm1").feature().remove("dmpDrive");}catch(Exception e){}
   m.study().create("stdEigCoupled");m.study("stdEigCoupled").create("eig","Eigenfrequency");
   m.study("stdEigCoupled").feature("eig").set("neigs","12");m.study("stdEigCoupled").feature("eig").set("shift","3.33[GHz]");m.study("stdEigCoupled").feature("eig").set("shiftactive","on");m.study("stdEigCoupled").createAutoSequences("all");
   System.out.println("EIG_BEGIN");
   m.study("stdEigCoupled").run();System.out.println("EIG_DONE");
   String[] ds=m.result().dataset().tags();String data=ds[ds.length-1];System.out.println("DATASET="+data);
   m.result().numerical().create("evEigC","EvalGlobal");m.result().numerical("evEigC").set("data",data);m.result().numerical("evEigC").set("looplevelinput",new String[]{"all"});m.result().numerical("evEigC").set("expr",new String[]{"freq"});
   double[][] re=m.result().numerical("evEigC").getReal();
   for(int j=0;j<re[0].length;j++)System.out.printf(java.util.Locale.US,"MODE f_GHz=%.9f%n",re[0][j]/1e9);
   m.result().table().create("tblEigC","Table");m.result().numerical("evEigC").set("table","tblEigC");m.result().numerical("evEigC").setResult();m.result().table("tblEigC").save("D:\\comsol_ao_run\\convergence\\Wap_6um_coupled_eigen_1Vshort.csv");
   m.save("D:\\comsol_ao_run\\convergence\\Wap_6um_coupled_eigen.mph");
  }catch(Throwable t){t.printStackTrace(System.out);}finally{ModelUtil.disconnect();}
 }
}
