import com.comsol.model.*;
import com.comsol.model.util.*;

/**
 * 3D shorted-grating IDT, one wavelength in x, finite aperture in z.
 * Period, stack and crystal axes are the 2D result. Not a 1 V drive and not Qm.
 */
public class Idt3d {
  static final String PZ = "D:\\COMSOL63\\Multiphysics\\data\\comsol_piezo_lib.mph";
  static final String BASIC = "D:\\COMSOL63\\Multiphysics\\data\\comsol_basic_material_lib.mph";
  static final String MEMS = "D:\\COMSOL63\\Multiphysics\\data\\comsol_mems_lib.mph";

  public static void main(String[] args) throws Exception {
    ModelUtil.initStandalone(true);
    Model model = ModelUtil.create("Model");
    model.modelPath("D:\\comsol_ao_run\\idt_3d");
    model.label("idt_3d.mph");
    try {
      build(model);
      solve(model);
    } catch (Throwable ex) {
      ex.printStackTrace(System.out);
    }
  }

  static void copyGroup(Material dst, Material src, String group, boolean create) {
    if (create) dst.propertyGroup().create(group, group);
    String[] names = src.propertyGroup(group).properties();
    for (int i = 0; i < names.length; i++) {
      try {
        dst.propertyGroup(group).set(names[i], src.propertyGroup(group).getStringArray(names[i]));
      } catch (Exception ex) {
        System.out.println("skip " + group + "." + names[i] + " " + ex.getMessage());
      }
    }
  }

  static void block(Model model, String tag, String sx, String sy, String sz, String px, String py, String pz) {
    model.geom("geom1").feature().create(tag, "Block");
    model.geom("geom1").feature(tag).set("size", new String[]{sx, sy, sz});
    model.geom("geom1").feature(tag).set("pos", new String[]{px, py, pz});
  }

  static void box(Model model, String tag, int dim, String xmin, String xmax, String ymin, String ymax, String zmin, String zmax) {
    model.component("comp1").selection().create(tag, "Box");
    model.component("comp1").selection(tag).set("entitydim", Integer.toString(dim));
    model.component("comp1").selection(tag).set("condition", "intersects");
    model.component("comp1").selection(tag).set("xmin", xmin);
    model.component("comp1").selection(tag).set("xmax", xmax);
    model.component("comp1").selection(tag).set("ymin", ymin);
    model.component("comp1").selection(tag).set("ymax", ymax);
    model.component("comp1").selection(tag).set("zmin", zmin);
    model.component("comp1").selection(tag).set("zmax", zmax);
  }

  static void build(Model model) throws Exception {
    model.param().set("p", "0.94[um]");
    model.param().set("hSi", "12[um]");
    model.param().set("hOx", "1[um]");
    model.param().set("hLn", "500[nm]");
    model.param().set("hAl", "100[nm]");
    model.param().set("duty", "0.25");
    model.param().set("Wap", "10[um]");
    model.param().set("z0", "2[um]");
    model.param().set("Wstack", "14[um]");

    model.modelNode().create("comp1");
    model.geom().create("geom1", 3);
    model.geom("geom1").lengthUnit("m");
    block(model, "bSi", "p", "hSi", "Wstack", "0", "0", "0");
    block(model, "bOx", "p", "hOx", "Wstack", "0", "hSi", "0");
    block(model, "bLn", "p", "hLn", "Wstack", "0", "hSi+hOx", "0");
    block(model, "bAp", "duty*p", "hAl", "Wap", "(p-2*duty*p)/4", "hSi+hOx+hLn", "z0");
    block(model, "bAn", "duty*p", "hAl", "Wap", "p/2+(p-2*duty*p)/4", "hSi+hOx+hLn", "z0");
    model.geom("geom1").run();

    box(model, "selSi", 3, "1[nm]", "p-1[nm]", "1[nm]", "hSi-1[nm]", "1[nm]", "Wstack-1[nm]");
    box(model, "selOx", 3, "1[nm]", "p-1[nm]", "hSi+1[nm]", "hSi+hOx-1[nm]", "1[nm]", "Wstack-1[nm]");
    box(model, "selLN", 3, "1[nm]", "p-1[nm]", "hSi+hOx+1[nm]", "hSi+hOx+hLn-1[nm]", "1[nm]", "Wstack-1[nm]");
    box(model, "selAl", 3, "1[nm]", "p-1[nm]", "hSi+hOx+hLn+1[nm]", "hSi+hOx+hLn+hAl-1[nm]", "z0+1[nm]", "z0+Wap-1[nm]");
    box(model, "selBot", 2, "-1[nm]", "p+1[nm]", "-1[nm]", "1[nm]", "-1[nm]", "Wstack+1[nm]");
    box(model, "selGp", 2, "(p-2*duty*p)/4-1[nm]", "(p-2*duty*p)/4+duty*p+1[nm]",
        "hSi+hOx+hLn-1[nm]", "hSi+hOx+hLn+1[nm]", "z0-1[nm]", "z0+Wap+1[nm]");
    box(model, "selGn", 2, "p/2+(p-2*duty*p)/4-1[nm]", "p/2+(p-2*duty*p)/4+duty*p+1[nm]",
        "hSi+hOx+hLn-1[nm]", "hSi+hOx+hLn+1[nm]", "z0-1[nm]", "z0+Wap+1[nm]");
    model.component("comp1").selection().create("selGnd", "Union");
    model.component("comp1").selection("selGnd").set("entitydim", "2");
    model.component("comp1").selection("selGnd").set("input", new String[]{"selGp", "selGn"});

    Model pz = ModelUtil.load("pz", PZ);
    Model basic = ModelUtil.load("basic", BASIC);
    Model mems = ModelUtil.load("mems", MEMS);
    Material ln = model.component("comp1").material().create("matLN", "Common");
    ln.label("Lithium Niobate");
    ln.selection().named("selLN");
    ln.set("basis", "on");
    ln.set("basisx", new String[]{"0", "1", "0"});
    ln.set("specifybasisy", "on");
    ln.set("basisy", new String[]{"-1", "0", "0"});
    copyGroup(ln, pz.material("lithium_niobate"), "def", false);
    copyGroup(ln, pz.material("lithium_niobate"), "StressCharge", true);
    Material al = model.component("comp1").material().create("matAl", "Common");
    al.label("Aluminum");
    al.selection().named("selAl");
    copyGroup(al, basic.material("aluminum"), "def", false);
    copyGroup(al, basic.material("aluminum"), "Enu", true);
    Material ox = model.component("comp1").material().create("matOx", "Common");
    ox.label("SiO2");
    ox.selection().named("selOx");
    copyGroup(ox, mems.material("sio2_-_silicon_oxide"), "def", false);
    copyGroup(ox, mems.material("sio2_-_silicon_oxide"), "Enu", true);
    Material si = model.component("comp1").material().create("matSi", "Common");
    si.label("Silicon");
    si.selection().named("selSi");
    copyGroup(si, basic.material("silicon"), "def", false);
    copyGroup(si, basic.material("silicon"), "Enu", true);
    ModelUtil.remove("pz");
    ModelUtil.remove("basic");
    ModelUtil.remove("mems");

    model.physics().create("solid", "SolidMechanics", "geom1");
    model.physics().create("es", "Electrostatics", "geom1");
    model.physics("es").selection().named("selLN");
    model.multiphysics().create("pze1", "PiezoelectricEffect", "geom1");
    model.physics("solid").create("pzm1", "PiezoelectricMaterialModel", 3);
    model.physics("solid").feature("pzm1").selection().named("selLN");
    try {
      model.physics("solid").prop("ShapeProperty").set("order_displacement", "1");
    } catch (Exception ex) {
      System.out.println("order " + ex.getMessage());
    }
    model.physics("solid").create("fix1", "Fixed", 2);
    model.physics("solid").feature("fix1").selection().named("selBot");
    model.physics("es").create("gnd1", "Ground", 2);
    model.physics("es").feature("gnd1").selection().named("selGnd");
    applyPeriodic(model);

    String[] ops = {"intLN", "intOx", "intSi", "intAl"};
    String[] sels = {"selLN", "selOx", "selSi", "selAl"};
    for (int i = 0; i < ops.length; i++) {
      model.component("comp1").cpl().create(ops[i], "Integration");
      model.component("comp1").cpl(ops[i]).selection().geom("geom1", 3);
      model.component("comp1").cpl(ops[i]).selection().named(sels[i]);
    }

    model.mesh().create("mesh1", "geom1");
    size(model, "szLN", "selLN", "150[nm]", "30[nm]");
    size(model, "szAl", "selAl", "80[nm]", "20[nm]");
    size(model, "szOx", "selOx", "400[nm]", "80[nm]");
    size(model, "szSi", "selSi", "2.5[um]", "400[nm]");
    model.mesh("mesh1").feature().create("ftet1", "FreeTet");
    model.mesh("mesh1").feature("ftet1").selection().geom("geom1", 3);
    model.mesh("mesh1").feature("ftet1").selection().all();
    model.mesh("mesh1").run();

    model.study().create("std1");
    model.study("std1").create("eig", "Eigenfrequency");
    model.study("std1").feature("eig").set("neigs", "12");
    model.study("std1").feature("eig").set("shift", "3.33[GHz]");
    model.study("std1").feature("eig").set("shiftactive", "on");
    model.study("std1").createAutoSequences("all");
    System.out.println("BUILD_OK");
  }

  static double[] facePoint(Model model, int f) {
    double[][][] tries = {
      {{0.2}, {0.2}},
      {{0.0}, {0.0}},
      {{0.2, 0.2}},
      {{0.5}, {0.0}}
    };
    RuntimeException last = null;
    for (int i = 0; i < tries.length; i++) {
      try {
        double[][] a = model.geom("geom1").faceX(f, tries[i]);
        if (a.length >= 3 && a[0].length == 1) return new double[]{a[0][0], a[1][0], a[2][0]};
        if (a.length == 1 && a[0].length >= 3) return new double[]{a[0][0], a[0][1], a[0][2]};
        if (a[0].length >= 3) return new double[]{a[0][0], a[0][1], a[0][2]};
        return new double[]{a[0][0], a[1][0], 0};
      } catch (RuntimeException ex) {
        last = ex;
      }
    }
    throw last;
  }

  static void applyPeriodic(Model model) {
    box(model, "selLeft", 2, "-1[nm]", "1[nm]", "-1[nm]", "hSi+hOx+hLn+hAl+1[nm]", "-1[nm]", "Wstack+1[nm]");
    box(model, "selRight", 2, "p-1[nm]", "p+1[nm]", "-1[nm]", "hSi+hOx+hLn+hAl+1[nm]", "-1[nm]", "Wstack+1[nm]");
    model.component("comp1").selection("selLeft").set("condition", "inside");
    model.component("comp1").selection("selRight").set("condition", "inside");
    box(model, "selLeftE", 2, "-1[nm]", "1[nm]", "hSi+hOx-1[nm]", "hSi+hOx+hLn+1[nm]", "-1[nm]", "Wstack+1[nm]");
    box(model, "selRightE", 2, "p-1[nm]", "p+1[nm]", "hSi+hOx-1[nm]", "hSi+hOx+hLn+1[nm]", "-1[nm]", "Wstack+1[nm]");
    model.component("comp1").selection("selLeftE").set("condition", "inside");
    model.component("comp1").selection("selRightE").set("condition", "inside");
    System.out.println("Nleft " + model.component("comp1").selection("selLeft").entities().length
        + " Nright " + model.component("comp1").selection("selRight").entities().length
        + " NleftE " + model.component("comp1").selection("selLeftE").entities().length);
    model.component("comp1").selection().create("selPer", "Union");
    model.component("comp1").selection("selPer").set("entitydim", "2");
    model.component("comp1").selection("selPer").set("input", new String[]{"selLeft", "selRight"});
    model.component("comp1").selection().create("selPerE", "Union");
    model.component("comp1").selection("selPerE").set("entitydim", "2");
    model.component("comp1").selection("selPerE").set("input", new String[]{"selLeftE", "selRightE"});
    model.physics("solid").create("pc1", "PeriodicCondition", 2);
    model.physics("solid").feature("pc1").selection().named("selPer");
    model.physics("es").create("pc1", "PeriodicCondition", 2);
    model.physics("es").feature("pc1").selection().named("selPerE");
  }

  static void applyPeriodicUnused(Model model) {
    int nF = model.geom("geom1").getNFaces();
    int[] left = new int[nF];
    int[] right = new int[nF];
    int nl = 0;
    int nr = 0;
    double pmax = 0;
    for (int f = 1; f <= nF; f++) {
      double[] a = facePoint(model, f);
      double x = a[0];
      if (x > pmax) pmax = x;
    }
    for (int f = 1; f <= nF; f++) {
      double[] a = facePoint(model, f);
      double x = a[0];
      if (Math.abs(x) < 1e-9) left[nl++] = f;
      if (Math.abs(x - pmax) < 1e-8) right[nr++] = f;
    }
    int[] use = new int[nl + nr];
    System.arraycopy(left, 0, use, 0, nl);
    System.arraycopy(right, 0, use, nl, nr);
    System.out.println("FACES left=" + nl + " right=" + nr);
    model.physics("solid").create("pc1", "PeriodicCondition", 2);
    model.physics("solid").feature("pc1").selection().set(use);
    int nE = model.geom("geom1").getNFaces();
    int[] eLeft = new int[nE];
    int[] eRight = new int[nE];
    int el = 0;
    int er = 0;
    for (int f = 1; f <= nF; f++) {
      double[] a = facePoint(model, f);
      double x = a[0];
      double y = a[1];
      if (y < 13.0e-6 || y > 13.5e-6) continue;
      if (Math.abs(x) < 1e-9) eLeft[el++] = f;
      if (Math.abs(x - pmax) < 1e-8) eRight[er++] = f;
    }
    int[] eUse = new int[el + er];
    System.arraycopy(eLeft, 0, eUse, 0, el);
    System.arraycopy(eRight, 0, eUse, el, er);
    System.out.println("EFACES " + eUse.length);
    model.physics("es").create("pc1", "PeriodicCondition", 2);
    model.physics("es").feature("pc1").selection().set(eUse);
  }

  static void size(Model model, String tag, String sel, String hmax, String hmin) {
    model.mesh("mesh1").feature().create(tag, "Size");
    model.mesh("mesh1").feature(tag).selection().geom("geom1", 3);
    model.mesh("mesh1").feature(tag).selection().named(sel);
    model.mesh("mesh1").feature(tag).set("hmaxactive", "on");
    model.mesh("mesh1").feature(tag).set("hminactive", "on");
    model.mesh("mesh1").feature(tag).set("hmax", hmax);
    model.mesh("mesh1").feature(tag).set("hmin", hmin);
  }

  static void solve(Model model) {
    try {
      model.study("std1").run();
      model.result().numerical().create("gev1", "EvalGlobal");
      model.result().numerical("gev1").set("expr", new String[]{
        "freq",
        "intLN(solid.Ws)", "intOx(solid.Ws)", "intSi(solid.Ws)", "intAl(solid.Ws)",
        "intLN(u^2)", "intLN(v^2)", "intLN(w^2)"
      });
      model.result().numerical("gev1").set("looplevelinput", new String[]{"all"});
      double[][] re = model.result().numerical("gev1").getReal();
      System.out.println("SHAPE " + re.length + " x " + re[0].length);
      boolean freqRow = Math.abs(re[0][0]) > 1e6 || Math.abs(re[0][Math.min(1, re[0].length - 1)]) > 1e6;
      int nMode = freqRow ? re[0].length : re.length;
      double k = 2 * Math.PI / 0.94e-6;
      for (int m = 0; m < nMode; m++) {
        double f = freqRow ? re[0][m] : re[m][0];
        double eL = Math.abs(freqRow ? re[1][m] : re[m][1]);
        double eO = Math.abs(freqRow ? re[2][m] : re[m][2]);
        double eS = Math.abs(freqRow ? re[3][m] : re[m][3]);
        double eA = Math.abs(freqRow ? re[4][m] : re[m][4]);
        double u2 = Math.abs(freqRow ? re[5][m] : re[m][5]);
        double v2 = Math.abs(freqRow ? re[6][m] : re[m][6]);
        double w2 = Math.abs(freqRow ? re[7][m] : re[m][7]);
        double et = eL + eO + eS + eA;
        double ut = u2 + v2 + w2;
        System.out.println(String.format(java.util.Locale.US,
            "ROW f_GHz=%.6f k_rad_m=%.6e fracLN=%.4f fracOx=%.4f fracSi=%.4f fracAl=%.4f pu=%.3f pv=%.3f pw=%.3f",
            f / 1e9, k, et > 0 ? eL / et : -1, et > 0 ? eO / et : -1, et > 0 ? eS / et : -1, et > 0 ? eA / et : -1,
            ut > 0 ? u2 / ut : -1, ut > 0 ? v2 / ut : -1, ut > 0 ? w2 / ut : -1));
      }
    } catch (Throwable ex) {
      System.out.println("FAIL");
      ex.printStackTrace(System.out);
    }
  }
}
