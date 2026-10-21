import com.comsol.model.*; import com.comsol.model.util.*;
public class DriveAperture6umV4 {
 public static void main(String[] a)throws Exception{
  ModelUtil.initStandalone(true);Model m=ModelUtil.load("d","D:\\comsol_ao_run\\convergence\\DriveAperture6umV3_d.mph");
  try{
   m.study("stdDrive3").feature("freq").set("plist","3.302763e9[Hz] 3.304413e9[Hz] 3.306063e9[Hz]");
   m.study("stdDrive3").run();
   String[] ds=m.result().dataset().tags();String data=ds[ds.length-1];System.out.println("DATASET="+data);
   m.result().numerical().create("evDrive4","EvalGlobal");m.result().numerical("evDrive4").set("data",data);m.result().numerical("evDrive4").set("looplevelinput",new String[]{"all"});
   m.result().numerical("evDrive4").set("expr",new String[]{"freq","intLN(abs(V))","intLN(abs(u))","intLN(abs(v))","intLN(abs(w))","intLN(abs(solid.eXX))","intLN(abs(solid.eYY))","intLN(abs(solid.eZZ))","intLN(1)"});
   double[][] re=m.result().numerical("evDrive4").getReal();
   for(int j=0;j<re[0].length;j++)System.out.printf(java.util.Locale.US,"ROW f_GHz=%.9f Vavg=%.6e uavg_pm=%.6e vavg_pm=%.6e wavg_pm=%.6e eXXavg=%.6e eYYavg=%.6e eZZavg=%.6e LNvol=%.6e%n",re[0][j]/1e9,re[1][j]/re[8][j],re[2][j]/re[8][j]*1e12,re[3][j]/re[8][j]*1e12,re[4][j]/re[8][j]*1e12,re[5][j]/re[8][j],re[6][j]/re[8][j],re[7][j]/re[8][j],re[8][j]);
   m.result().table().create("tblDrive4","Table");m.result().numerical("evDrive4").set("table","tblDrive4");m.result().numerical("evDrive4").setResult();m.result().table("tblDrive4").save("D:\\comsol_ao_run\\convergence\\Wap_6um_fine_driven_1V_3freq.csv");
   m.save("D:\\comsol_ao_run\\convergence\\Wap_6um_fine_driven_Model_3freq.mph");
  }catch(Throwable t){t.printStackTrace(System.out);}finally{ModelUtil.disconnect();}
 }
}
