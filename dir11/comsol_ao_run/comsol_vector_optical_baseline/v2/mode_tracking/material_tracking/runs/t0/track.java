import com.comsol.model.*;
import com.comsol.model.util.*;

/**
 * One step of the material continuation.
 *
 * The saved model is loaded, ONLY the electrode permittivity is replaced, and
 * the existing mode-analysis study is run again.  Geometry, mesh, LN tensor,
 * wavelength and solver settings are left untouched, so any change in the
 * spectrum comes from the electrode material alone.
 *
 * Nothing is deleted; the new model is saved next to the original.
 */
public class track {
  public static void main(String[] args) throws Exception {
    ModelUtil.initStandalone(true);
    Model m = ModelUtil.load("m", "D:/comsol_ao_run/comsol_vector_optical_baseline/v2/out/final_eqairFix.mph");
    System.out.println("LOADED D:/comsol_ao_run/comsol_vector_optical_baseline/v2/out/final_eqairFix.mph");
    String al = "1";
    System.out.println("EPS_EXPR " + al);

    String[] tags = new String[]{"matAlL", "matAlR"};
    for (String t : tags) {
      m.component("comp1").material(t).propertyGroup("def")
          .set("relpermittivity",
               new String[]{al, "0", "0", "0", al, "0", "0", "0", al});
    }
    // read back what the model actually holds, not what was intended
    for (String t : tags) {
      try {
        String[] v = m.component("comp1").material(t).propertyGroup("def")
            .getStringArray("relpermittivity");
        System.out.println("READBACK " + t + " " + java.util.Arrays.toString(v));
      } catch (Throwable e) {
        System.out.println("READBACK_FAILED " + t + " " + e.getMessage());
      }
    }

    System.out.println("SOLVE_BEGIN");
    m.study("std1").run();
    System.out.println("SOLVE_DONE");

    try {
      // the saved model already contains result nodes, so a fixed tag can
      // collide; remove any stale node first and use a distinct name
      String gt = "trackNeff";
      try { m.result().numerical().remove(gt); } catch (Throwable ignore) {}
      m.result().numerical().create(gt, "EvalGlobal");
      m.result().numerical(gt).set("data", "dset1");
      m.result().numerical(gt).set("expr",
          new String[]{"real(ewfd.neff)", "imag(ewfd.neff)",
                       "intRidge(ewfd.normE^2)/intAll(ewfd.normE^2)"});
      m.result().numerical(gt).set("looplevelinput", new String[]{"all"});
      double[][] v = m.result().numerical(gt).getReal();
      for (int j = 0; j < v[0].length; j++) {
        System.out.println(String.format(java.util.Locale.US,
            "NEFF mode=%d re=%.17g im=%.17g ridge=%.6f",
            j + 1, v[0][j], v[1][j], v[2][j]));
      }
      System.out.println("WMODES " + v[0].length);
    } catch (Throwable t) {
      System.out.println("POSTPROC_FAILED " + t.getMessage());
    } finally {
      m.save("D:/comsol_ao_run/comsol_vector_optical_baseline/v2/mode_tracking/material_tracking/out/track_t0.mph");
      System.out.println("SAVED D:/comsol_ao_run/comsol_vector_optical_baseline/v2/mode_tracking/material_tracking/out/track_t0.mph");
    }
    ModelUtil.disconnect();
  }
}
