import com.comsol.model.*;
import com.comsol.model.util.*;

/**
 * Minimal probe: can we evaluate field expressions at chosen coordinates in a
 * SAVED model, for ONE solution, without running the study?
 *
 * It deliberately tries a small number of property spellings and reports which
 * one works, instead of assuming an API shape.
 */
public class gen_probe {
  static Model m;

  static void tryInterp(String label, String[] coordProp, String[] coords) {
    try {
      m.result().numerical().create("pt", "Interp");
      m.result().numerical("pt").set("data", "dset1");
      m.result().numerical("pt").set("expr", new String[]{
          "real(ewfd.Ex)", "imag(ewfd.Ex)",
          "real(ewfd.Ey)", "imag(ewfd.Ey)",
          "real(ewfd.Ez)", "imag(ewfd.Ez)",
          "ewfd.normE", "dom"});
      m.result().numerical("pt").set("coord", coords);
      double[][] re = m.result().numerical("pt").getReal();
      System.out.println("INTERP_OK " + label + " dims=" + re.length
          + "x" + (re.length > 0 ? re[0].length : 0));
      for (int e = 0; e < re.length; e++) {
        StringBuilder sb = new StringBuilder("  expr[" + e + "]:");
        for (int p = 0; p < re[e].length; p++) {
          sb.append(String.format(java.util.Locale.US, " %.6e", re[e][p]));
        }
        System.out.println(sb.toString());
      }
    } catch (Throwable t) {
      System.out.println("INTERP_FAIL " + label + " : " + t.getMessage());
    }
  }

  public static void main(String[] a) throws Exception {
    ModelUtil.initStandalone(true);
    m = ModelUtil.load("m", "D:/comsol_ao_run/comsol_vector_optical_baseline/v2/out/final_nomA6.mph");
    System.out.println("LOADED");
    System.out.println("SOLS " + java.util.Arrays.toString(m.sol().tags()));
    System.out.println("DATASETS " + java.util.Arrays.toString(
        m.result().dataset().tags()));

    // three interior points, well away from interfaces:
    // ridge centre, left slab, air above the film
    String[] coords = new String[]{"1.29", "0.30", "0.50", "0.12", "2.90", "1.20"};
    tryInterp("coord-x,y-pairs", new String[]{"coord"}, coords);

    // does the dataset expose several solutions?
    try {
      System.out.println("DSET_SOL " + m.result().dataset("dset1").getString("solution"));
    } catch (Throwable t) {
      System.out.println("DSET_SOL unavailable: " + t.getMessage());
    }
    ModelUtil.disconnect();
  }
}
