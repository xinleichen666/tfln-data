import com.comsol.model.*;
import com.comsol.model.util.*;

/** Load a saved model and report what we can use for domain-aware export. */
public class inspect_model {
  public static void main(String[] a) throws Exception {
    String path = "D:/comsol_ao_run/comsol_vector_optical_baseline/v2/out/final_nomA6.mph";
    ModelUtil.initStandalone(true);
    Model m = ModelUtil.load("m", path);
    System.out.println("LOADED " + path);
    System.out.println("DATASETS " + java.util.Arrays.toString(
        m.result().dataset().tags()));
    System.out.println("SOLS " + java.util.Arrays.toString(m.sol().tags()));
    System.out.println("NDOM " + m.component("comp1").geom("geom1").getNDomains());
    for (String s : new String[]{"selRidge", "selSlabL", "selSlabR",
                                 "selAir", "selSolid", "selAlL", "selAlR"}) {
      try {
        System.out.println("SEL " + s + " "
            + java.util.Arrays.toString(m.component("comp1")
                .selection(s).entities()));
      } catch (Exception e) {
        System.out.println("SEL " + s + " absent");
      }
    }
    // does the solution dataset carry several modes?
    try {
      m.result().numerical().create("probe", "EvalGlobal");
      m.result().numerical("probe").set("data", "dset1");
      m.result().numerical("probe").set("expr", new String[]{"real(ewfd.neff)"});
      m.result().numerical("probe").set("looplevelinput", new String[]{"all"});
      double[][] v = m.result().numerical("probe").getReal();
      System.out.println("MODES " + v[0].length);
      for (int j = 0; j < Math.min(5, v[0].length); j++) {
        System.out.println("  neff[" + (j + 1) + "]=" + v[0][j]);
      }
    } catch (Throwable t) {
      System.out.println("MODEPROBE failed: " + t.getMessage());
    }
    ModelUtil.disconnect();
  }
}
