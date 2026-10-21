import com.comsol.model.*; import com.comsol.model.util.*;
public class ExtractDriveV3 {
 public static void main(String[] a)throws Exception{
  ModelUtil.initStandalone(true);
  Model m=ModelUtil.load("d","D:\\comsol_ao_run\\convergence\\DriveAperture6umV2_d.mph");
  try{
   String[] ds=m.result().dataset().tags(); String data=ds[ds.length-1];
   m.result().numerical().create("evExtract3","EvalGlobal");m.result().numerical("evExtract3").set("data",data);m.result().numerical("evExtract3").set("looplevelinput",new String[]{"all"});
   m.result().numerical("evExtract3").set("expr",new String[]{"freq","intLN(abs(V))","intLN(abs(u))","intLN(abs(v))","intLN(abs(w))","intLN(abs(solid.eXX))","intLN(abs(solid.eYY))","intLN(abs(solid.eZZ))","intLN(1)"});
   double[][] re=m.result().numerical("evExtract3").getReal();
   for(int j=0;j<re[0].length;j++)System.out.printf(java.util.Locale.US,"ROW f_GHz=%.9f V_int=%.6e u_int=%.6e v_int=%.6e w_int=%.6e eXX_int=%.6e eYY_int=%.6e eZZ_int=%.6e LNvol=%.6e%n",re[0][j]/1e9,re[1][j],re[2][j],re[3][j],re[4][j],re[5][j],re[6][j],re[7][j],re[8][j]);
   m.result().table().create("tblExtract3","Table");m.result().numerical("evExtract3").set("table","tblExtract3");m.result().numerical("evExtract3").setResult();
   m.result().table("tblExtract3").save("D:\\comsol_ao_run\\convergence\\Wap_6um_fine_driven_1V_corrected.csv");
  }catch(Throwable t){t.printStackTrace(System.out);}finally{ModelUtil.disconnect();}
 }
}
