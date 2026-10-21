import com.comsol.model.*;
import com.comsol.model.util.*;
import java.util.Locale;

/**
 * Step 1: 3D thin-slice check against the 2D suspended IDT.
 *
 * Geometry: one x-period p=2.58 um, LN 500 nm, Al 100 nm, duty 0.25.
 * The slice is periodic in x AND z; the Al strips run through the whole
 * z length Lz=0.5 um, so the aperture direction is "infinite" (kz=0).
 *
 * Four variants (each in its own fresh model):
 *   B: order 1, LN 150/40 nm, Al 80/20 nm   (same as current 3D)
 *   C: order 2, LN 150/40 nm, Al 80/20 nm
 *   D: order 2, LN  75/20 nm, Al 40/10 nm
 *   E: order 1, LN  40/ 8 nm, Al 40/ 8 nm   (linear, mesh density like 2D)
 *
 * Prints markers consumed by the post-processing step:
 *   VARIANT_BEGIN / ORDER_READBACK / SEL_Z / NUMELEM / NMODE
 *   ROW variant=... f_GHz=... k_rad_m=... fracLN=... fracAl=... pu=... pv=... pw=...
 *   VARIANT_FAIL / VARIANT_END
 */
public class Step1SliceCheck {

  static final String PZ = "D:\\COMSOL63\\Multiphysics\\data\\comsol_piezo_lib.mph";
  static final String BASIC = "D:\\COMSOL63\\Multiphysics\\data\\comsol_basic_material_lib.mph";

  public static void main(String[] args) {
    try {
      ModelUtil.initStandalone(true);
      System.out.println("STEP1_START");
      runVariant("B", 1, "150[nm]", "40[nm]", "80[nm]", "20[nm]", 150, 40, 80, 20);
      runVariant("C", 2, "150[nm]", "40[nm]", "80[nm]", "20[nm]", 150, 40, 80, 20);
      runVariant("D", 2, "75[nm]", "20[nm]", "40[nm]", "10[nm]", 75, 20, 40, 10);
      runVariant("E", 1, "40[nm]", "8[nm]", "40[nm]", "8[nm]", 40, 8, 40, 8);
      System.out.println("STEP1_DONE");
    } catch (Throwable ex) {
      System.out.println("STEP1_ABORT");
      ex.printStackTrace(System.out);
    }
  }

  static void runVariant(String variant, int order, String lnHmax, String lnHmin,
                         String alHmax, String alHmin, int lnHmaxNm, int lnHminNm,
                         int alHmaxNm, int alHminNm) {
    String tag = "Model" + variant;
    System.out.println("VARIANT_BEGIN variant=" + variant + " order=" + order
        + " LN_hmax_nm=" + lnHmaxNm + " LN_hmin_nm=" + lnHminNm
        + " Al_hmax_nm=" + alHmaxNm + " Al_hmin_nm=" + alHminNm);
    Model model = null;
    boolean ok = false;
    try {
      model = ModelUtil.create(tag);
      build(model, variant, order, lnHmax, lnHmin, alHmax, alHmin);
      solve(model, variant);
      ok = true;
    } catch (Throwable ex) {
      System.out.println("VARIANT_FAIL variant=" + variant + " reason=" + oneLine(ex));
      ex.printStackTrace(System.out);
    } finally {
      if (model != null) {
        try { ModelUtil.remove(tag); } catch (Throwable t) {}
      }
      System.out.println("VARIANT_END variant=" + variant + (ok ? "" : " failed=1"));
    }
  }

  static String oneLine(Throwable ex) {
    String s = ex.getClass().getSimpleName() + ": " + String.valueOf(ex.getMessage());
    s = s.replace('\n', ' ').replace('\r', ' ').replace(',', ';');
    if (s.length() > 220) s = s.substring(0, 220);
    return s;
  }

  static void copyGroup(Material dst, Material src, String group, boolean create) {
    if (create) dst.propertyGroup().create(group, group);
    String[] names = src.propertyGroup(group).properties();
    for (int i = 0; i < names.length; i++) {
      try {
        dst.propertyGroup(group).set(names[i], src.propertyGroup(group).getStringArray(names[i]));
      } catch (Exception ex) {
        System.out.println("skip " + group + "." + names[i]);
      }
    }
  }

  static void block(Model model, String tag, String sx, String sy, String sz,
                    String px, String py, String pz) {
    model.geom("geom1").feature().create(tag, "Block");
    model.geom("geom1").feature(tag).set("size", new String[]{sx, sy, sz});
    model.geom("geom1").feature(tag).set("pos", new String[]{px, py, pz});
  }

  static void box(Model model, String tag, int dim,
                  String xmin, String xmax, String ymin, String ymax,
                  String zmin, String zmax) {
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

  static int nSel(Model model, String tag) {
    try {
      return model.component("comp1").selection(tag).entities().length;
    } catch (Throwable t) {
      return -1;
    }
  }

  static void build(Model model, String variant, int order,
                    String lnHmax, String lnHmin, String alHmax, String alHmin) throws Exception {
    model.param().set("p", "2.58[um]");
    model.param().set("hLn", "500[nm]");
    model.param().set("hAl", "100[nm]");
    model.param().set("duty", "0.25");
    model.param().set("Lz", "0.5[um]");
    model.param().set("Wstack", "Lz");
    model.param().set("z0", "0");
    model.param().set("Wap", "Lz");

    model.modelNode().create("comp1");
    model.geom().create("geom1", 3);
    model.geom("geom1").lengthUnit("m");
    block(model, "bLn", "p", "hLn", "Wstack", "0", "0", "0");
    block(model, "bAp", "duty*p", "hAl", "Wap", "(p-2*duty*p)/4", "hLn", "z0");
    block(model, "bAn", "duty*p", "hAl", "Wap", "p/2+(p-2*duty*p)/4", "hLn", "z0");
    model.geom("geom1").run();

    box(model, "selLN", 3, "1[nm]", "p-1[nm]", "1[nm]", "hLn-1[nm]", "1[nm]", "Wstack-1[nm]");
    box(model, "selAl", 3, "1[nm]", "p-1[nm]", "hLn+1[nm]", "hLn+hAl-1[nm]", "z0+1[nm]", "z0+Wap-1[nm]");
    box(model, "selGp", 2, "(p-2*duty*p)/4-1[nm]", "(p-2*duty*p)/4+duty*p+1[nm]",
        "hLn-1[nm]", "hLn+1[nm]", "z0-1[nm]", "z0+Wap+1[nm]");
    box(model, "selGn", 2, "p/2+(p-2*duty*p)/4-1[nm]", "p/2+(p-2*duty*p)/4+duty*p+1[nm]",
        "hLn-1[nm]", "hLn+1[nm]", "z0-1[nm]", "z0+Wap+1[nm]");
    model.component("comp1").selection().create("selGnd", "Union");
    model.component("comp1").selection("selGnd").set("entitydim", "2");
    model.component("comp1").selection("selGnd").set("input", new String[]{"selGp", "selGn"});

    Model pz = ModelUtil.load("pz", PZ);
    Model basic = ModelUtil.load("basic", BASIC);
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
    ModelUtil.remove("pz");
    ModelUtil.remove("basic");

    model.physics().create("solid", "SolidMechanics", "geom1");
    model.physics().create("es", "Electrostatics", "geom1");
    model.physics("es").selection().named("selLN");
    model.multiphysics().create("pze1", "PiezoelectricEffect", "geom1");
    model.physics("solid").create("pzm1", "PiezoelectricMaterialModel", 3);
    model.physics("solid").feature("pzm1").selection().named("selLN");

    String orderStr = Integer.toString(order);
    try {
      model.physics("solid").prop("ShapeProperty").set("order_displacement", orderStr);
    } catch (Throwable ex) {
      System.out.println("ORDER_SET_FAIL variant=" + variant + " reason=" + oneLine(ex));
      throw new RuntimeException("order_displacement set failed: " + oneLine(ex));
    }
    System.out.println("ORDER_READBACK variant=" + variant + " order=" + orderStr
        + " read=" + readOrder(model));

    model.physics("es").create("gnd1", "Ground", 2);
    model.physics("es").feature("gnd1").selection().named("selGnd");

    // x-periodic boundaries (same as Idt3dSus.java)
    box(model, "selLeft", 2, "-1[nm]", "1[nm]", "-1[nm]", "hLn+hAl+1[nm]", "-1[nm]", "Wstack+1[nm]");
    box(model, "selRight", 2, "p-1[nm]", "p+1[nm]", "-1[nm]", "hLn+hAl+1[nm]", "-1[nm]", "Wstack+1[nm]");
    box(model, "selLeftE", 2, "-1[nm]", "1[nm]", "-1[nm]", "hLn+1[nm]", "-1[nm]", "Wstack+1[nm]");
    box(model, "selRightE", 2, "p-1[nm]", "p+1[nm]", "-1[nm]", "hLn+1[nm]", "-1[nm]", "Wstack+1[nm]");
    model.component("comp1").selection("selLeft").set("condition", "inside");
    model.component("comp1").selection("selRight").set("condition", "inside");
    model.component("comp1").selection("selLeftE").set("condition", "inside");
    model.component("comp1").selection("selRightE").set("condition", "inside");
    System.out.println("SEL_X variant=" + variant + " selLeft=" + nSel(model, "selLeft")
        + " selRight=" + nSel(model, "selRight") + " selLeftE=" + nSel(model, "selLeftE")
        + " selRightE=" + nSel(model, "selRightE"));
    model.component("comp1").selection().create("selPer", "Union");
    model.component("comp1").selection("selPer").set("entitydim", "2");
    model.component("comp1").selection("selPer").set("input", new String[]{"selLeft", "selRight"});
    model.component("comp1").selection().create("selPerE", "Union");
    model.component("comp1").selection("selPerE").set("entitydim", "2");
    model.component("comp1").selection("selPerE").set("input", new String[]{"selLeftE", "selRightE"});

    // z-periodic boundaries: thin slice <=> kz = 0
    box(model, "selZ0", 2, "-1[nm]", "p+1[nm]", "-1[nm]", "hLn+hAl+1[nm]", "-1[nm]", "1[nm]");
    box(model, "selZ1", 2, "-1[nm]", "p+1[nm]", "-1[nm]", "hLn+hAl+1[nm]", "Lz-1[nm]", "Lz+1[nm]");
    box(model, "selZ0E", 2, "-1[nm]", "p+1[nm]", "-1[nm]", "hLn+1[nm]", "-1[nm]", "1[nm]");
    box(model, "selZ1E", 2, "-1[nm]", "p+1[nm]", "-1[nm]", "hLn+1[nm]", "Lz-1[nm]", "Lz+1[nm]");
    model.component("comp1").selection("selZ0").set("condition", "inside");
    model.component("comp1").selection("selZ1").set("condition", "inside");
    model.component("comp1").selection("selZ0E").set("condition", "inside");
    model.component("comp1").selection("selZ1E").set("condition", "inside");
    int nZ0 = nSel(model, "selZ0");
    int nZ1 = nSel(model, "selZ1");
    int nZ0E = nSel(model, "selZ0E");
    int nZ1E = nSel(model, "selZ1E");
    System.out.println("SEL_Z variant=" + variant + " selZ0=" + nZ0 + " selZ1=" + nZ1
        + " selZ0E=" + nZ0E + " selZ1E=" + nZ1E);
    if (nZ0 <= 0 || nZ1 <= 0 || nZ0E <= 0 || nZ1E <= 0) {
      throw new RuntimeException("empty z selection (selZ0=" + nZ0 + ",selZ1=" + nZ1
          + ",selZ0E=" + nZ0E + ",selZ1E=" + nZ1E + ")");
    }
    model.component("comp1").selection().create("selPerZ", "Union");
    model.component("comp1").selection("selPerZ").set("entitydim", "2");
    model.component("comp1").selection("selPerZ").set("input", new String[]{"selZ0", "selZ1"});
    model.component("comp1").selection().create("selPerZE", "Union");
    model.component("comp1").selection("selPerZE").set("entitydim", "2");
    model.component("comp1").selection("selPerZE").set("input", new String[]{"selZ0E", "selZ1E"});

    model.physics("solid").create("pc1", "PeriodicCondition", 2);
    model.physics("solid").feature("pc1").selection().named("selPer");
    model.physics("es").create("pc1", "PeriodicCondition", 2);
    model.physics("es").feature("pc1").selection().named("selPerE");
    model.physics("solid").create("pc2", "PeriodicCondition", 2);
    model.physics("solid").feature("pc2").selection().named("selPerZ");
    model.physics("es").create("pc2", "PeriodicCondition", 2);
    model.physics("es").feature("pc2").selection().named("selPerZE");

    model.component("comp1").cpl().create("intLN", "Integration");
    model.component("comp1").cpl("intLN").selection().geom("geom1", 3);
    model.component("comp1").cpl("intLN").selection().named("selLN");
    model.component("comp1").cpl().create("intAl", "Integration");
    model.component("comp1").cpl("intAl").selection().geom("geom1", 3);
    model.component("comp1").cpl("intAl").selection().named("selAl");

    model.mesh().create("mesh1", "geom1");
    size(model, "szLN", "selLN", lnHmax, lnHmin);
    size(model, "szAl", "selAl", alHmax, alHmin);
    model.mesh("mesh1").feature().create("ftet1", "FreeTet");
    model.mesh("mesh1").feature("ftet1").selection().geom("geom1", 3);
    model.mesh("mesh1").feature("ftet1").selection().all();
    model.mesh("mesh1").run();

    int nElem = -1;
    try {
      nElem = model.mesh("mesh1").getNumElem();
    } catch (Throwable t) {
      nElem = -1;
    }
    System.out.println("NUMELEM variant=" + variant + " n_elem=" + (nElem > 0 ? Integer.toString(nElem) : "NA"));

    model.study().create("std1");
    model.study("std1").create("eig", "Eigenfrequency");
    model.study("std1").feature("eig").set("neigs", "12");
    model.study("std1").feature("eig").set("shift", "3.33[GHz]");
    model.study("std1").feature("eig").set("shiftactive", "on");
    model.study("std1").createAutoSequences("all");
    System.out.println("BUILD_OK variant=" + variant);
  }

  static String readOrder(Model model) {
    Object p;
    try {
      p = model.physics("solid").prop("ShapeProperty");
    } catch (Throwable t) {
      return "unavailable(no-prop)";
    }
    try {
      java.lang.reflect.Method m = p.getClass().getMethod("getString", String.class);
      Object v = m.invoke(p, "order_displacement");
      if (v != null) return String.valueOf(v);
    } catch (Throwable t) {}
    try {
      java.lang.reflect.Method m = p.getClass().getMethod("getStringArray", String.class);
      Object v = m.invoke(p, "order_displacement");
      if (v instanceof String[]) {
        String[] a = (String[]) v;
        return a.length > 0 ? a[0] : "empty";
      }
    } catch (Throwable t) {}
    try {
      String s = String.valueOf(p);
      if (s != null && s.contains("order_displacement")) return "toString:" + s;
    } catch (Throwable t) {}
    return "unavailable(write-only)";
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

  static void solve(Model model, String variant) {
    model.study("std1").run();
    model.result().numerical().create("gev1", "EvalGlobal");
    model.result().numerical("gev1").set("expr", new String[]{
      "freq", "intLN(solid.Ws)", "intAl(solid.Ws)", "intLN(u^2)", "intLN(v^2)", "intLN(w^2)"
    });
    model.result().numerical("gev1").set("looplevelinput", new String[]{"all"});
    double[][] re = model.result().numerical("gev1").getReal();
    int nMode = re[0].length;
    System.out.println("NMODE variant=" + variant + " n=" + nMode);
    double k = 2 * Math.PI / 2.58e-6;
    for (int m = 0; m < nMode; m++) {
      double f = re[0][m];
      double eL = Math.abs(re[1][m]);
      double eA = Math.abs(re[2][m]);
      double u2 = Math.abs(re[3][m]);
      double v2 = Math.abs(re[4][m]);
      double w2 = Math.abs(re[5][m]);
      double et = eL + eA;
      double ut = u2 + v2 + w2;
      System.out.println(String.format(Locale.US,
          "ROW variant=%s f_GHz=%.6f k_rad_m=%.6e fracLN=%.4f fracAl=%.4f pu=%.3f pv=%.3f pw=%.3f",
          variant, f / 1e9, k, et > 0 ? eL / et : -1, et > 0 ? eA / et : -1,
          ut > 0 ? u2 / ut : -1, ut > 0 ? v2 / ut : -1, ut > 0 ? w2 / ut : -1));
    }
  }
}
