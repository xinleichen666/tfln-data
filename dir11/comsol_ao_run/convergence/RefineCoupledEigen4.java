import com.comsol.model.*; import com.comsol.model.util.*;
public class RefineCoupledEigen4 { public static void main(String[] a)throws Exception{
 ModelUtil.initStandalone(true);Model m=ModelUtil.load("m","D:\\comsol_ao_run\\convergence\\Wap_6um_coupled_eigen_refined.mph");
 try{
  m.mesh("mesh1").feature("szLN").set("hmax","65[nm]");m.mesh("mesh1").feature("szLN").set("hmin","16[nm]");m.mesh("mesh1").feature("szAl").set("hmax","33[nm]");m.mesh("mesh1").feature("szAl").set("hmin","8[nm]");
  System.out.println("MESH_BEGIN");m.mesh("mesh1").run();System.out.println("MESH_DONE");System.out.println("EIG_BEGIN");m.study("stdEigCoupled").run();System.out.println("EIG_DONE");
  String[]ds=m.result().dataset().tags();String data=ds[ds.length-1];m.result().numerical().create("evalFine4","EvalGlobal");m.result().numerical("evalFine4").set("data",data);m.result().numerical("evalFine4").set("looplevelinput",new String[]{"all"});m.result().numerical("evalFine4").set("expr",new String[]{"freq"});double[][]fs=m.result().numerical("evalFine4").getReal();
  m.result().table().create("tblFine4","Table");m.result().numerical("evalFine4").set("table","tblFine4");m.result().numerical("evalFine4").setResult();m.result().table("tblFine4").save("D:\\comsol_ao_run\\convergence\\Wap_6um_coupled_eigen_refined4.csv");
  int j=1;String tag="ref4M2";m.result().export().create(tag,"Data");m.result().export(tag).set("data",data);m.result().export(tag).set("looplevelinput",new String[]{"manual"});m.result().export(tag).set("looplevel",new String[]{"2"});m.result().export(tag).set("expr",new String[]{"x","y","z","u","v","w"});String file=String.format(java.util.Locale.US,"D:\\comsol_ao_run\\convergence\\mode_match\\refined4_mode02_%.6fGHz.csv",fs[0][j]/1e9);m.result().export(tag).set("filename",file);m.result().export(tag).set("header","on");m.result().export(tag).set("sort","on");m.result().export(tag).run();System.out.println("EXPORTED "+file);m.save("D:\\comsol_ao_run\\convergence\\Wap_6um_coupled_eigen_refined4.mph");
 }catch(Throwable t){t.printStackTrace(System.out);}finally{ModelUtil.disconnect();}
}}
