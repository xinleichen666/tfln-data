import com.comsol.model.*;
import com.comsol.model.util.*;

/**
 * Export one mode from a SAVED model together with its domain index.
 *
 * The domain number is exported as the expression `dom`, so the downstream
 * reader can group points by actual COMSOL domain instead of guessing from
 * geometric boxes.
 */
public class __CLASS__ {
  public static void main(String[] a) throws Exception {
    String model = "__MODEL__";
    String tag = "__TAG__";
    int mode = __MODE__;
    String out = "__OUT__";

    ModelUtil.initStandalone(true);
    Model m = ModelUtil.load("m", model);
    System.out.println("LOADED " + model);
    for (String s : new String[]{"selRidge", "selSlabL", "selSlabR",
                                 "selAir", "selSolid", "selMetal",
                                 "selAlL", "selAlR"}) {
      try {
        System.out.println("SELMAP " + s + "="
            + java.util.Arrays.toString(m.component("comp1")
                .selection(s).entities()));
      } catch (Exception e) {
        System.out.println("SELMAP " + s + "=absent");
      }
    }
    System.out.println("NDOM " + m.component("comp1").geom("geom1").getNDomains());
    System.out.println("MODES_TOTAL "
        + m.result().numerical("g1").getReal()[0].length);

    m.result().export().create("xdom", "Data");
    m.result().export("xdom").set("data", "dset1");
    m.result().export("xdom").set("looplevelinput", new String[]{"manual"});
    m.result().export("xdom").set("looplevel",
        new String[]{Integer.toString(mode)});
    m.result().export("xdom").set("expr", new String[]{
        "dom", "ewfd.normE",
        "real(ewfd.Ex)", "imag(ewfd.Ex)",
        "real(ewfd.Ey)", "imag(ewfd.Ey)",
        "real(ewfd.Ez)", "imag(ewfd.Ez)"});
    m.result().export("xdom").set("filename", out);
    m.result().export("xdom").run();
    System.out.println("EXPORTED " + out);

    m.result().numerical().create("chk", "EvalGlobal");
    m.result().numerical("chk").set("data", "dset1");
    m.result().numerical("chk").set("expr",
        new String[]{"real(ewfd.neff)", "imag(ewfd.neff)"});
    m.result().numerical("chk").set("looplevelinput", new String[]{"manual"});
    m.result().numerical("chk").set("looplevel",
        new String[]{Integer.toString(mode)});
    double[][] v = m.result().numerical("chk").getReal();
    System.out.println(String.format(java.util.Locale.US,
        "MODENEFF mode=%d re=%.6f im=%.6e", mode, v[0][0], v[1][0]));
    ModelUtil.disconnect();
  }
}
