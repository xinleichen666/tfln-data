import com.comsol.model.*; import com.comsol.model.util.*;
public class ExtractDriveV2 {
 public static void main(String[] a)throws Exception{
  ModelUtil.initStandalone(true);
  Model m=ModelUtil.load("d","D:\\comsol_ao_run\\convergence\\DriveAperture6umV2_d.mph");
  try{
   String[] ds=m.result().dataset().tags(); String data=ds[ds.length-1];
   System.out.println("DATASET="+data+" ALL="+java.util.Arrays.toString(ds));
   m.component("comp1").cpl().create("maxLN","Maximum");
   m.component("comp1").cpl("maxLN").selection().geom("geom1",3);
   m.component("comp1").cpl("maxLN").selection().named("selLN");
   m.result().numerical().create("evExtract","EvalGlobal");m.result().numerical("evExtract").set("data",data);m.result().numerical("evExtract").set("looplevelinput",new String[]{"all"});
   m.result().numerical("evExtract").set("expr",new String[]{"freq","intLN(abs(V))","intLN(abs(u))","intLN(abs(v))","intLN(abs(w))","maxLN(sqrt(u^2+v^2+w^2))","maxLN(abs(solid.eXX))","maxLN(abs(solid.eYY))","maxLN(abs(solid.eZZ))","maxLN(abs(V))"});
   double[][] re=m.result().numerical("evExtract").getReal();
   for(int j=0;j<re[0].length;j++)System.out.printf(java.util.Locale.US,"ROW f_GHz=%.9f V_int=%.6e u_int=%.6e v_int=%.6e w_int=%.6e umax_nm=%.6e eXXmax=%.6e eYYmax=%.6e eZZmax=%.6e Vmax=%.6e%n",re[0][j]/1e9,re[1][j],re[2][j],re[3][j],re[4][j],re[5][j]*1e9,re[6][j],re[7][j],re[8][j],re[9][j]);
   m.result().table().create("tblExtract","Table");m.result().numerical("evExtract").set("table","tblExtract");m.result().numerical("evExtract").setResult();
   m.result().table("tblExtract").save("D:\\comsol_ao_run\\convergence\\Wap_6um_fine_driven_1V_corrected.csv");
   m.save("D:\\comsol_ao_run\\convergence\\Wap_6um_fine_driven_Model_corrected.mph");
  }catch(Throwable t){t.printStackTrace(System.out);}finally{ModelUtil.disconnect();}
 }
}
