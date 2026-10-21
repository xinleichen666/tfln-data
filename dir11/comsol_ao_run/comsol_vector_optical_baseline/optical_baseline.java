import com.comsol.model.*;
import com.comsol.model.util.*;

/**
 * Full-vector mode analysis of the candidate TFLN acousto-optic cross-section.
 *
 * Geometry (um), matching the acoustic model's coordinate convention:
 *   x in [0, 2.58]  one acoustic period
 *   y in [0, 0.5]   LN film; ridge in the metal-free channel
 *   ridge  : x 0.9675..1.6125, y 0..0.5
 *   slab   : x 0..0.9675 and 1.6125..2.58, y 0..0.25
 *   Al     : x 0.3225..0.9675 and 1.6125..2.2575, y 0.25..0.35
 *   air    : everything else, extended 1.6 um beyond the film in x
 *
 * Light propagates along z, the crystal optic axis, so both in-plane
 * polarisations see n_o; the model therefore uses an isotropic n_o = 2.211.
 * Al is treated with a complex index (bulk screening value).
 *
 * Modes: Mode Analysis at 1550 nm, complex eigenvalue problem.
 *
 * Usage: java optical_baseline metal hmax_nm xw_um tag
 */
public class optical_gen {
  static final String OUT = "D:/comsol_ao_run/comsol_vector_optical_baseline";
  static Model active;
  static double NO = 2.211;
  static double KAPPA_AL = 15.6;
  static double N_AL_RE = 1.44;

  static void box(Model m, String tag, double x0, double x1, double y0, double y1) {
    m.component("comp1").selection().create(tag, "Box");
    m.component("comp1").selection(tag).set("entitydim", "2");
    m.component("comp1").selection(tag).set("condition", "inside");
    m.component("comp1").selection(tag).set("xmin", x0 + "[um]");
    m.component("comp1").selection(tag).set("xmax", x1 + "[um]");
    m.component("comp1").selection(tag).set("ymin", y0 + "[um]");
    m.component("comp1").selection(tag).set("ymax", y1 + "[um]");
  }

  static void rect(GeomSequence g, String tag, double x0, double y0,
                   double w, double h) {
    g.create(tag, "Rectangle");
    g.feature(tag).set("size", new String[]{w + "[um]", h + "[um]"});
    g.feature(tag).set("pos", new String[]{x0 + "[um]", y0 + "[um]"});
  }

  static void eps(String tag, String expr) {
    active.component("comp1").physics("ewfd").feature(tag)
        .set("DisplacementFieldModel", "RelativePermittivity");
    active.component("comp1").physics("ewfd").feature(tag)
        .set("epsilonr_mat", "userdef");
    active.component("comp1").physics("ewfd").feature(tag)
        .set("epsilonr", new String[]{expr});
    active.component("comp1").physics("ewfd").feature(tag)
        .set("mur_mat", "userdef");
    active.component("comp1").physics("ewfd").feature(tag)
        .set("mur", new String[]{"1"});
    active.component("comp1").physics("ewfd").feature(tag)
        .set("sigma_mat", "userdef");
    active.component("comp1").physics("ewfd").feature(tag)
        .set("sigma", new String[]{"0"});
  }

  static void material(Model m, String tag, String sel, String nExpr,
                       String sigma) {
    m.component("comp1").material().create(tag, "Common");
    m.component("comp1").material(tag).selection().named(sel);
    String n2 = "(" + nExpr + ")^2";
    m.component("comp1").material(tag).propertyGroup("def")
        .set("relpermittivity", new String[]{n2, "0", "0", "0", n2, "0",
                                             "0", "0", n2});
    m.component("comp1").material(tag).propertyGroup("def")
        .set("relpermeability", new String[]{"1", "0", "0", "0", "1", "0",
                                             "0", "0", "1"});
    m.component("comp1").material(tag).propertyGroup("def")
        .set("electricconductivity", new String[]{sigma, "0", "0", "0", sigma,
                                                  "0", "0", "0", sigma});
  }

  static void override(String tag, String sel, String expr) {
    active.component("comp1").physics("ewfd").create(tag, "WaveEquationElectric", 2);
    active.component("comp1").physics("ewfd").feature(tag).selection().named(sel);
    eps(tag, expr);
    int[] e = active.component("comp1").physics("ewfd").feature(tag)
        .selection().entities();
    int[] s = active.component("comp1").selection(sel).entities();
    System.out.println("SEL " + tag + " box=" + java.util.Arrays.toString(s)
        + " physics=" + java.util.Arrays.toString(e));
  }


  public static void main(String[] args) throws Exception {
    boolean metal = __METAL__;
    double hmax = __HMAX__;
    double xw = __XW__;
    String tag = "__TAG__";
    System.out.println("CONFIG metal=" + metal + " hmax=" + hmax
        + "nm xw=" + xw + "um tag=" + tag);

    ModelUtil.initStandalone(true);
    Model m = ModelUtil.create("Model");
    active = m;
    m.label("optical_baseline_" + tag);
    m.param().set("lda0", "1.55[um]");
    m.param().set("f0", "c_const/lda0");

    m.component().create("comp1", true);
    m.component("comp1").geom().create("geom1", 2);
    m.component("comp1").geom("geom1").lengthUnit("um");
    GeomSequence g = m.component("comp1").geom("geom1");

    rect(g, "air", -xw, -1.0, 2.58 + 2 * xw, 2.6);
    rect(g, "slabL", 0.0, 0.0, 0.9675, 0.25);
    rect(g, "slabR", 1.6125, 0.0, 0.9675, 0.25);
    rect(g, "ridge", 0.9675, 0.0, 0.645, 0.5);
    if (metal) {
      rect(g, "alL", 0.3225, 0.25, 0.645, 0.1);
      rect(g, "alR", 1.6125, 0.25, 0.645, 0.1);
    }
    g.run();
    System.out.println("GEOM domains " + m.component("comp1").geom("geom1").getNDomains());

    box(m, "selRidge", 0.9674, 1.6126, -0.001, 0.501);
    box(m, "selSlabL", -0.001, 0.9676, -0.001, 0.251);
    box(m, "selSlabR", 1.6124, 2.581, -0.001, 0.251);
    if (metal) {
      box(m, "selAlL", 0.3224, 0.9676, 0.2499, 0.3501);
      box(m, "selAlR", 1.6124, 2.2576, 0.2499, 0.3501);
    }

    box(m, "selAll", -10, 10, -10, 10);
    m.component("comp1").selection().create("selSolid", "Union");
    m.component("comp1").selection("selSolid").set("entitydim", "2");
    m.component("comp1").selection("selSolid").set("input",
        metal ? new String[]{"selRidge", "selSlabL", "selSlabR", "selAlL", "selAlR"}
              : new String[]{"selRidge", "selSlabL", "selSlabR"});
    m.component("comp1").selection().create("selAir", "Difference");
    m.component("comp1").selection("selAir").set("entitydim", "2");
    m.component("comp1").selection("selAir").set("add", new String[]{"selAll"});
    m.component("comp1").selection("selAir").set("subtract",
        new String[]{"selSolid"});
    System.out.println("SEL solid="
        + java.util.Arrays.toString(m.component("comp1").selection("selSolid").entities())
        + " air="
        + java.util.Arrays.toString(m.component("comp1").selection("selAir").entities()));
    m.component("comp1").physics().create("ewfd",
        "ElectromagneticWavesFrequencyDomain", "geom1");
    material(m, "matAir", "selAir", "1", "0");
    String ln = "(" + NO + "-__LNK__*i)";
    material(m, "matRidge", "selRidge", ln, "0");
    material(m, "matSlabL", "selSlabL", ln, "0");
    material(m, "matSlabR", "selSlabR", ln, "0");
    if (metal) {
      String al = "(" + N_AL_RE + "__ALSIGN__" + KAPPA_AL + "*i)";
      material(m, "matAlL", "selAlL", al, "0");
      material(m, "matAlR", "selAlR", al, "0");
    }

    m.component("comp1").mesh().create("mesh1", "geom1");
    m.component("comp1").mesh("mesh1").feature("size").set("hauto", "5");
    m.component("comp1").mesh("mesh1").feature("size").set("custom", "on");
    m.component("comp1").mesh("mesh1").feature("size").set("hmax", hmax + "[nm]");
    m.component("comp1").mesh("mesh1").feature("size").set("hmin", "2[nm]");
    m.component("comp1").mesh("mesh1").create("ftri1", "FreeTri");
    m.component("comp1").mesh("mesh1").run();
    int ne = m.component("comp1").mesh("mesh1").getElem("tri")[0].length;
    System.out.println("MESH tri " + ne + " hmax " + hmax);

    m.study().create("std1");
    m.study("std1").create("mode", "ModeAnalysis");
    m.study("std1").feature("mode").set("modeFreq", "f0");
    m.study("std1").feature("mode").set("neigsactive", true);
    m.study("std1").feature("mode").set("neigs", 40);
    m.study("std1").feature("mode").set("shiftactive", true);
    m.study("std1").feature("mode").set("shift", "__SHIFT__");
    m.study("std1").createAutoSequences("all");
    System.out.println("SOLVE_BEGIN");
    m.study("std1").run();
    System.out.println("SOLVE_DONE");

    m.result().numerical().create("gev1", "EvalGlobal");
    m.result().numerical("gev1").set("data", "dset1");
    m.result().numerical("gev1").set("expr",
        new String[]{"real(ewfd.neff)", "imag(ewfd.neff)", "ewfd.dampz"});
    m.result().numerical("gev1").set("looplevelinput", new String[]{"all"});
    // all three expressions are real-valued, so read them from getReal()
    double[][] v = m.result().numerical("gev1").getReal();
    for (int j = 0; j < v[0].length; j++) {
      System.out.println(String.format(java.util.Locale.US,
          "NEFF mode=%d re=%.6f im=%.6e dampz=%.6e",
          j + 1, v[0][j], v[1][j], v[2][j]));
    }
    Integer[] order = new Integer[v[0].length];
    for (int j = 0; j < order.length; j++) order[j] = j;
    final double[] neffArr = v[0];
    java.util.Arrays.sort(order, (a, b) -> Double.compare(neffArr[b], neffArr[a]));
    System.out.println("TOP neff=" + v[0][order[0]] + " mode=" + (order[0] + 1));

    int nexport = Math.min(6, order.length);
    for (int q = 0; q < nexport; q++) {
      int m2 = order[q] + 1;
      String et = "m" + m2;
      m.result().export().create(et, "Data");
      m.result().export(et).set("data", "dset1");
      m.result().export(et).set("looplevelinput", new String[]{"manual"});
      m.result().export(et).set("looplevel",
          new String[]{Integer.toString(m2)});
      m.result().export(et).set("expr", new String[]{"ewfd.normE"});
      m.result().export(et).set("filename",
          OUT + "/out/f_" + tag + "_" + et + ".csv");
      m.result().export(et).run();
      System.out.println("FIELD mode=" + m2 + " neff=" + v[0][order[q]]
          + " -> f_" + tag + "_" + et + ".csv");
    }
    m.save(OUT + "/out/optical_" + tag + ".mph");
    System.out.println("SAVED " + OUT + "/out/optical_" + tag + ".mph");
  }
}

