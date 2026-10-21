import com.comsol.model.*; import com.comsol.model.util.*;
public class ExportCoupledModes {
 static void run(String in, String prefix, String out) throws Exception {
  Model m=ModelUtil.load("m",in);
  String[] ds=m.result().dataset().tags(); String data=ds[ds.length-1];
  System.out.println("DATA="+data+" datasets="+java.util.Arrays.toString(ds));
  m.result().numerical().create("evalF","EvalGlobal");
  m.result().numerical("evalF").set("data",data);
  m.result().numerical("evalF").set("looplevelinput",new String[]{"all"});
  m.result().numerical("evalF").set("expr",new String[]{"freq"});
  double[][] f=m.result().numerical("evalF").getReal();
  System.out.println("NMODES="+f[0].length);
  for(int j=0;j<f[0].length;j++) {
   String tag="expmatch"+(j+1); m.result().export().create(tag,"Data");
   m.result().export(tag).set("data",data);
   m.result().export(tag).set("looplevelinput",new String[]{"manual"});
   m.result().export(tag).set("looplevel",new String[]{Integer.toString(j+1)});
   m.result().export(tag).set("expr",new String[]{"x","y","z","u","v","w"});
   String file=out+"\\"+prefix+String.format(java.util.Locale.US,"_mode%02d_%.6fGHz.csv",j+1,f[0][j]/1e9);
   m.result().export(tag).set("filename",file); m.result().export(tag).set("header","on"); m.result().export(tag).set("sort","on");
   m.result().export(tag).run(); System.out.println("EXPORTED "+file);
  }
  ModelUtil.remove("m");
 }
 public static void main(String[] a) throws Exception {
  ModelUtil.initStandalone(true);
  try {run("D:\\comsol_ao_run\\convergence\\Wap_6um_coupled_eigen.mph","fine","D:\\comsol_ao_run\\convergence\\mode_match"); run("D:\\comsol_ao_run\\convergence\\Wap_6um_coupled_eigen_coarse.mph","coarse","D:\\comsol_ao_run\\convergence\\mode_match");}
  catch(Throwable t){t.printStackTrace(System.out);} finally{ModelUtil.disconnect();}
 }
}


