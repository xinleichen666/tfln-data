import com.comsol.model.*; import com.comsol.model.util.*;
public class RefineCoupledEigen {
 public static void main(String[] a)throws Exception{
  ModelUtil.initStandalone(true); Model m=ModelUtil.load("m","D:\\comsol_ao_run\\convergence\\Wap_6um_coupled_eigen.mph");
  try{
   m.mesh("mesh1").feature("szLN").set("hmax","75[nm]");m.mesh("mesh1").feature("szLN").set("hmin","18[nm]");
   m.mesh("mesh1").feature("szAl").set("hmax","38[nm]");m.mesh("mesh1").feature("szAl").set("hmin","9[nm]");
   System.out.println("MESH_BEGIN");m.mesh("mesh1").run();System.out.println("MESH_DONE");
   System.out.println("EIG_BEGIN");m.study("stdEigCoupled").run();System.out.println("EIG_DONE");
   String[] ds=m.result().dataset().tags();String data=ds[ds.length-1];System.out.println("DATA="+data);
   m.result().numerical().create("evalFine3","EvalGlobal");m.result().numerical("evalFine3").set("data",data);m.result().numerical("evalFine3").set("looplevelinput",new String[]{"all"});m.result().numerical("evalFine3").set("expr",new String[]{"freq"});double[][] fs=m.result().numerical("evalFine3").getReal();
   m.result().table().create("tblFine3","Table");m.result().numerical("evalFine3").set("table","tblFine3");m.result().numerical("evalFine3").setResult();m.result().table("tblFine3").save("D:\\comsol_ao_run\\convergence\\Wap_6um_coupled_eigen_refined.csv");
   for(int j=0;j<fs[0].length;j++){
    String tag="refM"+(j+1);m.result().export().create(tag,"Data");m.result().export(tag).set("data",data);m.result().export(tag).set("looplevelinput",new String[]{"manual"});m.result().export(tag).set("looplevel",new String[]{Integer.toString(j+1)});m.result().export(tag).set("expr",new String[]{"x","y","z","u","v","w"});String file=String.format(java.util.Locale.US,"D:\\comsol_ao_run\\convergence\\mode_match\\refined_mode%02d_%.6fGHz.csv",j+1,fs[0][j]/1e9);m.result().export(tag).set("filename",file);m.result().export(tag).set("header","on");m.result().export(tag).set("sort","on");m.result().export(tag).run();System.out.println("EXPORTED "+file);
   }
   m.save("D:\\comsol_ao_run\\convergence\\Wap_6um_coupled_eigen_refined.mph");
  }catch(Throwable t){t.printStackTrace(System.out);}finally{ModelUtil.disconnect();}
 }
}
