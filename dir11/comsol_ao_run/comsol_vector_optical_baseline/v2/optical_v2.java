import com.comsol.model.*;
import com.comsol.model.util.*;

/**
 * v2 optical baseline.  Scope is fixed and deliberately small.
 *
 * Cross-section (um), one acoustic period in x:
 *   film   : y 0..0.5, x 0..2.58
 *   ridge  : x 0.9675..1.6125, y 0..0.5
 *   slab   : x 0..0.9675 and 1.6125..2.58, y 0..0.25
 *   Al     : x 0.3225..0.9675 and 1.6125..2.2575, y 0.25..0.35
 *
 * Light along z (the crystal optic axis).  LN is anisotropic:
 *   eps = diag(n_o^2, n_o^2, n_e^2)  in the model frame.
 * Al is a complex index with a NEGATIVE imaginary part, because this model
 * was calibrated to give Im(neff) < 0 and dampz > 0 for absorption.
 *
 * No conductivity parameter: at optical frequencies the metal is described by
 * a complex permittivity, and an earlier conductivity attempt had no effect.
 */
public class __CLASS__ {
  static final String OUT = "D:/comsol_ao_run/comsol_vector_optical_baseline/v2";
  static Model active;
  static final double NO = 2.211;
  static final double NE = 2.138;
  static final double KAPPA_AL = 15.6;
  static final double N_AL_RE = 1.44;

  static void box(Model m, String tag, double x0, double x1,
                  double y0, double y1) {
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

  /** Material with a diagonal relative permittivity tensor. */
  static void material(Model m, String tag, String sel,
                       String exx, String eyy, String ezz) {
    m.component("comp1").material().create(tag, "Common");
    m.component("comp1").material(tag).selection().named(sel);
    m.component("comp1").material(tag).propertyGroup("def")
        .set("relpermittivity", new String[]{exx, "0", "0", "0", eyy, "0",
                                             "0", "0", ezz});
    m.component("comp1").material(tag).propertyGroup("def")
        .set("relpermeability", new String[]{"1", "0", "0", "0", "1", "0",
                                             "0", "0", "1"});
    // required by the Relative permittivity formulation; zero here because
    // metallic loss is carried by the imaginary part of the permittivity
    m.component("comp1").material(tag).propertyGroup("def")
        .set("electricconductivity", new String[]{"0", "0", "0", "0", "0", "0",
                                                  "0", "0", "0"});
  }


  public static void main(String[] args) throws Exception {
    boolean metal = __METAL__;
    double hmax = __HMAX__;
    double xw = __XW__;
    String shift = "__SHIFT__";
    String tag = "__TAG__";
    System.out.println("CONFIG metal=" + metal + " hmax=" + hmax
        + " xw=" + xw + " shift=" + shift + " tag=" + tag);

    ModelUtil.initStandalone(true);
    Model m = ModelUtil.create("Model");
    active = m;
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
    System.out.println("GEOM domains "
        + m.component("comp1").geom("geom1").getNDomains());

    box(m, "selRidge", 0.9674, 1.6126, -0.001, 0.501);
    box(m, "selSlabL", -0.001, 0.9676, -0.001, 0.251);
    box(m, "selSlabR", 1.6124, 2.581, -0.001, 0.251);
    box(m, "selAll", -10, 10, -10, 10);
    if (metal) {
      box(m, "selAlL", 0.3224, 0.9676, 0.2499, 0.3501);
      box(m, "selAlR", 1.6124, 2.2576, 0.2499, 0.3501);
      m.component("comp1").selection().create("selMetal", "Union");
      m.component("comp1").selection("selMetal").set("entitydim", "2");
      m.component("comp1").selection("selMetal").set("input",
          new String[]{"selAlL", "selAlR"});
    }
    m.component("comp1").selection().create("selSolid", "Union");
    m.component("comp1").selection("selSolid").set("entitydim", "2");
    m.component("comp1").selection("selSolid").set("input",
        metal ? new String[]{"selRidge", "selSlabL", "selSlabR",
                             "selAlL", "selAlR"}
              : new String[]{"selRidge", "selSlabL", "selSlabR"});
    m.component("comp1").selection().create("selAir", "Difference");
    m.component("comp1").selection("selAir").set("entitydim", "2");
    m.component("comp1").selection("selAir").set("add",
        new String[]{"selAll"});
    m.component("comp1").selection("selAir").set("subtract",
        new String[]{"selSolid"});
    int[] solid = m.component("comp1").selection("selSolid").entities();
    int[] air = m.component("comp1").selection("selAir").entities();
    System.out.println("SEL solid=" + java.util.Arrays.toString(solid)
        + " air=" + java.util.Arrays.toString(air));
    if (solid.length == 0 || air.length == 0) {
      throw new IllegalStateException("empty domain selection");
    }



    m.component("comp1").physics().create("ewfd",
        "ElectromagneticWavesFrequencyDomain", "geom1");
    // the default model is Refractive index; a permittivity tensor requires
    // the Relative permittivity formulation, otherwise COMSOL tries to convert
    // the anisotropic tensor to an isotropic index and fails
    try {
      m.component("comp1").physics("ewfd").feature("wee1")
          .set("DisplacementFieldModel", "RelativePermittivity");
      System.out.println("EWFD model = RelativePermittivity");
    } catch (Throwable t) {
      System.out.println("EWFD model set FAILED: " + t.getMessage());
    }
    String no2 = String.valueOf(NO * NO);
    String nzz = __ANISO__ ? String.valueOf(NE * NE) : no2;
    String al = "__ALEPS__";
    material(m, "matAir", "selAir", "1", "1", "1");
    material(m, "matRidge", "selRidge", no2, no2, nzz);
    material(m, "matSlabL", "selSlabL", no2, no2, nzz);
    material(m, "matSlabR", "selSlabR", no2, no2, nzz);
    if (metal) {
      material(m, "matAlL", "selAlL", al, al, al);
      material(m, "matAlR", "selAlR", al, al, al);
    }

    // integration operators must exist before the model is solved
    m.component("comp1").cpl().create("intRidge", "Integration");
    m.component("comp1").cpl("intRidge").selection().geom("geom1", 2);
    m.component("comp1").cpl("intRidge").selection().named("selRidge");
    m.component("comp1").cpl().create("intAll", "Integration");
    m.component("comp1").cpl("intAll").selection().geom("geom1", 2);
    m.component("comp1").cpl("intAll").selection().all();
    if (metal) {
      m.component("comp1").cpl().create("intAl", "Integration");
      m.component("comp1").cpl("intAl").selection().geom("geom1", 2);
      m.component("comp1").cpl("intAl").selection().named("selMetal");
    }

    m.component("comp1").mesh().create("mesh1", "geom1");
    m.component("comp1").mesh("mesh1").feature("size").set("hauto", "5");
    m.component("comp1").mesh("mesh1").feature("size").set("custom", "on");
    m.component("comp1").mesh("mesh1").feature("size")
        .set("hmax", hmax + "[nm]");
    m.component("comp1").mesh("mesh1").feature("size").set("hmin", "2[nm]");
    m.component("comp1").mesh("mesh1").create("ftri1", "FreeTri");
    m.component("comp1").mesh("mesh1").run();
    System.out.println("MESH tri "
        + m.component("comp1").mesh("mesh1").getElem("tri")[0].length);

    m.study().create("std1");
    m.study("std1").create("mode", "ModeAnalysis");
    m.study("std1").feature("mode").set("modeFreq", "c_const/1.55[um]");
    m.study("std1").feature("mode").set("neigsactive", true);
    m.study("std1").feature("mode").set("neigs", __NEIGS__);
    m.study("std1").feature("mode").set("shiftactive", true);
    m.study("std1").feature("mode").set("shift", shift);
    m.study("std1").createAutoSequences("all");
    System.out.println("SOLVE_BEGIN");
    m.study("std1").run();
    System.out.println("SOLVE_DONE");
    m.save(OUT + "/out/solved_" + tag + ".mph");
    System.out.println("SAVED_SOLVED " + OUT + "/out/solved_" + tag + ".mph");



    // ---- post-processing: everything is guarded so a failure cannot lose the solve
    try {
      m.result().numerical().create("g1", "EvalGlobal");
      m.result().numerical("g1").set("data", "dset1");
      m.result().numerical("g1").set("expr", new String[]{
          "real(ewfd.neff)", "imag(ewfd.neff)", "ewfd.dampz",
          "intRidge(ewfd.normE^2)/intAll(ewfd.normE^2)"});
      m.result().numerical("g1").set("looplevelinput", new String[]{"all"});
      double[][] v = m.result().numerical("g1").getReal();
      for (int j = 0; j < v[0].length; j++) {
        System.out.println(String.format(java.util.Locale.US,
            "NEFF mode=%d re=%.6f im=%.6e dampz=%.6e ridge=%.4f",
            j + 1, v[0][j], v[1][j], v[2][j], v[3][j]));
      }
      Integer[] order = new Integer[v[0].length];
      for (int j = 0; j < order.length; j++) order[j] = j;
      final double[] neff = v[0];
      java.util.Arrays.sort(order,
          (a, b) -> Double.compare(neff[b], neff[a]));
      System.out.println("TOP mode=" + (order[0] + 1) + " neff=" + v[0][order[0]]);

      if (metal && m.component("comp1").cpl().tags().length > 0) {
        try {
          m.result().numerical().create("g2", "EvalGlobal");
          m.result().numerical("g2").set("data", "dset1");
          m.result().numerical("g2").set("expr", new String[]{
              "intAl(ewfd.Qh)", "intAll(ewfd.Poavz)"});
          m.result().numerical("g2").set("looplevelinput",
              new String[]{"all"});
          double[][] eb = m.result().numerical("g2").getReal();
          for (int j = 0; j < eb[0].length; j++) {
            System.out.println(String.format(java.util.Locale.US,
                "ENERGY mode=%d Pdiss=%.6e Pflow=%.6e", j + 1,
                eb[0][j], eb[1][j]));
          }
        } catch (Throwable t2) {
          System.out.println("ENBAL_FAILED " + t2.getMessage());
        }
      }

      int nexport = Math.min(__NEXPORT__, order.length);
      for (int q = 0; q < nexport; q++) {
        int mi = order[q] + 1;
        String et = "x" + mi;
        m.result().export().create(et, "Data");
        m.result().export(et).set("data", "dset1");
        m.result().export(et).set("looplevelinput", new String[]{"manual"});
        m.result().export(et).set("looplevel",
            new String[]{Integer.toString(mi)});
        m.result().export(et).set("expr", new String[]{
            "ewfd.normE", "real(ewfd.Ex)", "imag(ewfd.Ex)",
            "real(ewfd.Ey)", "imag(ewfd.Ey)",
            "real(ewfd.Ez)", "imag(ewfd.Ez)"});
        m.result().export(et).set("filename",
            OUT + "/out/f_" + tag + "_m" + mi + ".csv");
        m.result().export(et).run();
        System.out.println("FIELD mode=" + mi + " neff=" + v[0][order[q]]
            + " -> f_" + tag + "_m" + mi + ".csv");
      }
      System.out.println("POSTPROC_OK");
    } catch (Throwable t) {
      System.out.println("POSTPROC_FAILED " + t.getMessage());
      t.printStackTrace(System.out);
    } finally {
      m.save(OUT + "/out/final_" + tag + ".mph");
      System.out.println("SAVED_FINAL " + OUT + "/out/final_" + tag + ".mph");
    }
  }
}

