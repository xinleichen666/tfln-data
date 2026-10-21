import com.comsol.model.*;
import com.comsol.model.util.*;
public class probe2 {
  public static void main(String[] a) throws Exception {
    ModelUtil.initStandalone(true);
    Model m = ModelUtil.load("m", "D:/comsol_ao_run/comsol_vector_optical_baseline/v2/out/final_nomA6.mph");
    String[] sels = new String[]{"selAir","selSlabL","selRidge","selSlabR"};
    for (String s : sels) {
      try {
        String t = "is" + s;
        m.result().numerical().create(t, "IntSurface");
        m.result().numerical(t).set("data", "dset1");
        m.result().numerical(t).selection().named(s);
        m.result().numerical(t).set("expr", new String[]{"1","ewfd.normE^2"});
        m.result().numerical(t).set("looplevelinput", new String[]{"manual"});
        m.result().numerical(t).set("looplevel", new String[]{"40"});
        double[][] v = m.result().numerical(t).getReal();
        System.out.println("OK " + s + " area_um2=" + String.format(java.util.Locale.US, "%.12g", v[0][0]*1e12) + " normE2_um2=" + String.format(java.util.Locale.US, "%.12g", v[1][0]*1e12));
      } catch (Throwable e) {
        System.out.println("NO " + s + " : " + String.valueOf(e.getMessage()).replace('\n',' '));
      }
    }
    System.out.println("PROBE2_DONE");
    ModelUtil.disconnect();
  }
}
