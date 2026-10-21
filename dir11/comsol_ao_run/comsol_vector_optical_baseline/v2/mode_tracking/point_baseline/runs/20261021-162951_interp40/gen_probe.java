import com.comsol.model.*;
import com.comsol.model.util.*;

/**
 * Minimal probe: evaluate field expressions at chosen coordinates in a SAVED
 * model, for ONE solution, without running the study.
 *
 * API from the COMSOL 6.3 reference for Interp:
 *   coord   double matrix, columns are evaluation points
 *   solnum  nonnegative integer array, selects the solutions
 *   ext     extrapolation distance (0 disables extrapolation)
 *   getData() returns result[expression][solnum][coordinates]
 */
public class gen_probe {
  public static void main(String[] a) throws Exception {
    ModelUtil.initStandalone(true);
    Model m = ModelUtil.load("m", "D:/comsol_ao_run/comsol_vector_optical_baseline/v2/out/final_nomA6.mph");
    System.out.println("LOADED");
    System.out.println("DATASETS " + java.util.Arrays.toString(
        m.result().dataset().tags()));
    try {
      System.out.println("DSET_SOL "
          + m.result().dataset("dset1").getString("solution"));
    } catch (Throwable t) {
      System.out.println("DSET_SOL unavailable: " + t.getMessage());
    }

    // ridge centre (1.29, 0.30), left slab (0.50, 0.12), air above (2.90, 1.20)
    double[][] coord = new double[][]{
        {1.29, 0.50, 2.90},
        {0.30, 0.12, 1.20}};

    int solnum = 40;
    m.result().numerical().create("pt", "Interp");
    m.result().numerical("pt").set("data", "dset1");
    m.result().numerical("pt").set("solnum", new int[]{solnum});
    m.result().numerical("pt").set("coord", coord);
    m.result().numerical("pt").set("ext", 0.0);
    m.result().numerical("pt").set("expr", new String[]{
        "real(ewfd.Ex)", "imag(ewfd.Ex)",
        "real(ewfd.Ey)", "imag(ewfd.Ey)",
        "real(ewfd.Ez)", "imag(ewfd.Ez)",
        "ewfd.normE", "dom"});
    m.result().numerical("pt").run();

    double[][][] re = m.result().numerical("pt").getData();
    System.out.println("INTERP_OK expr=" + re.length + " sol="
        + re[0].length + " points=" + re[0][0].length);
    for (int e = 0; e < re.length; e++) {
      StringBuilder sb = new StringBuilder("  expr[" + e + "]:");
      for (int p = 0; p < re[e][0].length; p++) {
        sb.append(String.format(java.util.Locale.US, " %.6e", re[e][0][p]));
      }
      System.out.println(sb.toString());
    }

    m.result().numerical().create("nchk", "EvalGlobal");
    m.result().numerical("nchk").set("data", "dset1");
    m.result().numerical("nchk").set("expr",
        new String[]{"real(ewfd.neff)", "imag(ewfd.neff)"});
    m.result().numerical("nchk").set("looplevelinput", new String[]{"manual"});
    m.result().numerical("nchk").set("looplevel",
        new String[]{Integer.toString(solnum)});
    double[][] v = m.result().numerical("nchk").getReal();
    System.out.println(String.format(java.util.Locale.US,
        "MODENEFF sol=%d re=%.6f im=%.6e", solnum, v[0][0], v[1][0]));

    ModelUtil.disconnect();
  }
}
