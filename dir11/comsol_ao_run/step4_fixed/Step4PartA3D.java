import com.comsol.model.*;
import com.comsol.model.util.*;
import java.lang.reflect.*;
import java.util.Arrays;
import java.util.Locale;

/** Step 4 Part A, 3D: fixed orientation (sys2) and ground selection (inside). */
public class Step4PartA3D {
  static final String PZ = "D:\\COMSOL63\\Multiphysics\\data\\comsol_piezo_lib.mph";
  static final String BASIC = "D:\\COMSOL63\\Multiphysics\\data\\comsol_basic_material_lib.mph";

  public static void main(String[] args) {
    try {
      ModelUtil.initStandalone(true);
      System.out.println("STEP4_3D_START");
      runVariant("3D-A", "75[nm]", "20[nm]", "40[nm]", "10[nm]", 75, 20, true);
      runVariant("3D-B", "75[nm]", "20[nm]", "40[nm]", "10[nm]", 75, 20, false);
      runVariant("3D-C", "60[nm]", "15[nm]", "30[nm]", "8[nm]", 60, 15, false);
      System.out.println("STEP4_3D_DONE");
    } catch (Throwable t) {
      System.out.println("STEP4_3D_ABORT");
      t.printStackTrace(System.out);
    }
  }

  static void runVariant(String variant, String lnHmax, String lnHmin, String alHmax, String alHmin,
                         int lnHmaxNm, int lnHminNm, boolean w0) {
    String tag = "M4D" + variant.replace("-", "");
    System.out.println("VARIANT_BEGIN variant=" + variant + " dim=3 part=A setting=" + (w0 ? "w0" : "free")
        + " LN_hmax_nm=" + lnHmaxNm + " LN_hmin_nm=" + lnHminNm + " orient=sys");
    Model model = null;
    boolean ok = false;
    try {
      model = ModelUtil.create(tag);
      build(model, variant, lnHmax, lnHmin, alHmax, alHmin, w0);
      solve(model, variant);
      ok = true;
    } catch (Throwable ex) {
      System.out.println("VARIANT_FAIL variant=" + variant + " reason=" + oneLine(ex));
      ex.printStackTrace(System.out);
    } finally {
      if (model != null) { try { ModelUtil.remove(tag); } catch (Throwable t) {} }
      System.out.println("VARIANT_END variant=" + variant + (ok ? "" : " failed=1"));
    }
  }

  static String oneLine(Throwable ex) {
    Throwable c = (ex instanceof InvocationTargetException) ? ((InvocationTargetException) ex).getTargetException() : ex;
    String s = c.getClass().getSimpleName() + ": " + String.valueOf(c.getMessage());
    s = s.replace('\n', ' ').replace('\r', ' ').replace(',', ';');
    if (s.length() > 260) s = s.substring(0, 260);
    return s;
  }

  static void copyGroup(Material dst, Material src, String group, boolean create) {
    if (create) dst.propertyGroup().create(group, group);
    String[] names = src.propertyGroup(group).properties();
    for (int i = 0; i < names.length; i++) {
      try { dst.propertyGroup(group).set(names[i], src.propertyGroup(group).getStringArray(names[i])); }
      catch (Exception ex) { System.out.println("skip " + group + "." + names[i]); }
    }
  }

  static void block(Model model, String tag, String sx, String sy, String sz, String px, String py, String pz) {
    model.geom("geom1").feature().create(tag, "Block");
    model.geom("geom1").feature(tag).set("size", new String[]{sx, sy, sz});
    model.geom("geom1").feature(tag).set("pos", new String[]{px, py, pz});
  }

  static void box(Model model, String tag, int dim, String xmin, String xmax,
                  String ymin, String ymax, String zmin, String zmax, String cond) {
    model.component("comp1").selection().create(tag, "Box");
    model.component("comp1").selection(tag).set("entitydim", Integer.toString(dim));
    model.component("comp1").selection(tag).set("condition", cond);
    model.component("comp1").selection(tag).set("xmin", xmin);
    model.component("comp1").selection(tag).set("xmax", xmax);
    model.component("comp1").selection(tag).set("ymin", ymin);
    model.component("comp1").selection(tag).set("ymax", ymax);
    model.component("comp1").selection(tag).set("zmin", zmin);
    model.component("comp1").selection(tag).set("zmax", zmax);
  }

  static Object call(Object o, String meth) {
    try { return o.getClass().getMethod(meth).invoke(o); }
    catch (Throwable t) { return "ERR:" + oneLine(unwrap(t)); }
  }
  static String getStr(Object o, String n) {
    try { return (String) o.getClass().getMethod("getString", String.class).invoke(o, n); }
    catch (Throwable t) { return "ERR"; }
  }
  static String[] getStrArr(Object o, String n) {
    try { return (String[]) o.getClass().getMethod("getStringArray", String.class).invoke(o, n); }
    catch (Throwable t) { return new String[]{"ERR"}; }
  }
  static void setStr(Object o, String n, String v) throws Exception {
    o.getClass().getMethod("set", String.class, String.class).invoke(o, n, v);
  }
  static void setArr(Object o, String n, String[] v) throws Exception {
    o.getClass().getMethod("set", String.class, String[].class).invoke(o, n, v);
  }
  static Throwable unwrap(Throwable t) {
    if (t instanceof InvocationTargetException) return ((InvocationTargetException) t).getTargetException();
    return t;
  }
  static int nSel(Model model, String tag) {
    try { return model.component("comp1").selection(tag).entities().length; }
    catch (Throwable t) { return -1; }
  }

  static void setupSys(Model model) throws Exception {
    Object sys = model.component("comp1").coordSystem().create("sys2", "Rotated");
    String[] sysProps = (String[]) call(sys, "properties");
    System.out.println("DIAG_SYS2_PROPS = " + Arrays.toString(sysProps));
    for (int i = 0; i < sysProps.length; i++) {
      String v = getStr(sys, sysProps[i]);
      if (v.equals("ERR")) {
        try { v = Arrays.toString((String[]) sys.getClass().getMethod("getStringArray", String.class).invoke(sys, sysProps[i])); } catch (Throwable t) {}
      }
      System.out.println("DIAG_SYS2_VAL " + sysProps[i] + " = " + v);
    }
    setStr(sys, "rotationSequence", "ZXZ");
    setArr(sys, "angle", new String[]{"90[deg]", "0", "0"});
    System.out.println("SYS2_SET angle=" + getStr(sys, "angle") + " seq=" + getStr(sys, "rotationSequence"));
    Object pz = model.physics("solid").feature("pzm1");
    Object cc = model.physics("es").feature("ccp1");
    System.out.println("DEFAULT_COORD pzm1=" + getStr(pz, "coordinateSystem") + " ccp1=" + getStr(cc, "coordinateSystem"));
    setStr(pz, "coordinateSystem", "sys2");
    setStr(cc, "coordinateSystem", "sys2");
    System.out.println("COORD_SYS_SET pzm1=" + getStr(pz, "coordinateSystem") + " ccp1=" + getStr(cc, "coordinateSystem"));
  }

  static void checkGroundFace(Model model, String tag, String variant) throws Exception {
    int[] ents = model.component("comp1").selection(tag).entities();
    System.out.println("GROUND_CHECK variant=" + variant + " tag=" + tag + " n=" + ents.length);
    Method fm = model.geom("geom1").getClass().getMethod("faceX", int.class, double[][].class);
    Method pr = model.geom("geom1").getClass().getMethod("faceParamRange", int.class);
    for (int i = 0; i < ents.length; i++) {
      double[] range = (double[]) pr.invoke(model.geom("geom1"), ents[i]);
      double u0 = range[0], u1 = range[1], v0 = range[2], v1 = range[3];
      double[][] pairs = new double[][]{{u0, v0}, {u1, v0}, {u0, v1}, {u1, v1},
        {0.5 * (u0 + u1), 0.5 * (v0 + v1)}};
      double[][] xyz = (double[][]) fm.invoke(model.geom("geom1"), ents[i], pairs);
      double xmin = 1e9, xmax = -1e9, ymin = 1e9, ymax = -1e9, zmin = 1e9, zmax = -1e9;
      for (int k = 0; k < xyz.length; k++) {
        xmin = Math.min(xmin, xyz[k][0]); xmax = Math.max(xmax, xyz[k][0]);
        ymin = Math.min(ymin, xyz[k][1]); ymax = Math.max(ymax, xyz[k][1]);
        zmin = Math.min(zmin, xyz[k][2]); zmax = Math.max(zmax, xyz[k][2]);
      }
      System.out.println(String.format(Locale.US,
          "GROUND_FACE variant=%s tag=%s id=%d x=[%.6e,%.6e] y=[%.6e,%.6e] z=[%.6e,%.6e]",
          variant, tag, ents[i], xmin, xmax, ymin, ymax, zmin, zmax));
    }
  }

  static void build(Model model, String variant, String lnHmax, String lnHmin,
                    String alHmax, String alHmin, boolean w0) throws Exception {
    model.param().set("p", "2.8326[um]");
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

    box(model, "selLN", 3, "1[nm]", "p-1[nm]", "1[nm]", "hLn-1[nm]", "1[nm]", "Wstack-1[nm]", "intersects");
    box(model, "selAl", 3, "1[nm]", "p-1[nm]", "hLn+1[nm]", "hLn+hAl-1[nm]", "z0+1[nm]", "z0+Wap-1[nm]", "intersects");
    box(model, "selGp", 2, "(p-2*duty*p)/4-1[nm]", "(p-2*duty*p)/4+duty*p+1[nm]",
        "hLn-1[nm]", "hLn+1[nm]", "z0-1[nm]", "z0+Wap+1[nm]", "inside");
    box(model, "selGn", 2, "p/2+(p-2*duty*p)/4-1[nm]", "p/2+(p-2*duty*p)/4+duty*p+1[nm]",
        "hLn-1[nm]", "hLn+1[nm]", "z0-1[nm]", "z0+Wap+1[nm]", "inside");
    model.component("comp1").selection().create("selGnd", "Union");
    model.component("comp1").selection("selGnd").set("entitydim", "2");
    model.component("comp1").selection("selGnd").set("input", new String[]{"selGp", "selGn"});

    Model pz = ModelUtil.load("pz", PZ);
    Model basic = ModelUtil.load("basic", BASIC);
    Material ln = model.component("comp1").material().create("matLN", "Common");
    ln.selection().named("selLN");
    copyGroup(ln, pz.material("lithium_niobate"), "def", false);
    copyGroup(ln, pz.material("lithium_niobate"), "StressCharge", true);
    Material al = model.component("comp1").material().create("matAl", "Common");
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
    model.physics("es").create("ccp1", "ChargeConservationPiezo", 3);
    model.physics("es").feature("ccp1").selection().named("selLN");
    setupSys(model);

    model.physics("solid").feature("pzm1").create("dmp1", "Damping", 3);
    model.physics("solid").feature("pzm1").feature("dmp1").set("DampingType", "IsotropicLossFactor");
    model.physics("solid").feature("pzm1").feature("dmp1").set("eta_s_mat", "userdef");
    model.physics("solid").feature("pzm1").feature("dmp1").set("eta_s", "5e-4");
    try { model.physics("solid").prop("ShapeProperty").set("order_displacement", "2"); }
    catch (Throwable ex) { System.out.println("ORDER_SET_FAIL " + oneLine(ex)); }
    System.out.println("ORDER_READBACK order=" + getStr(model.physics("solid").prop("ShapeProperty"), "order_displacement"));

    model.physics("es").create("gnd1", "Ground", 2);
    model.physics("es").feature("gnd1").selection().named("selGnd");
    checkGroundFace(model, "selGp", variant);
    checkGroundFace(model, "selGn", variant);
    if (nSel(model, "selGp") != 1 || nSel(model, "selGn") != 1) {
      throw new RuntimeException("ground face check failed: selGp=" + nSel(model, "selGp") + " selGn=" + nSel(model, "selGn"));
    }

    box(model, "selLeft", 2, "-1[nm]", "1[nm]", "-1[nm]", "hLn+hAl+1[nm]", "-1[nm]", "Wstack+1[nm]", "inside");
    box(model, "selRight", 2, "p-1[nm]", "p+1[nm]", "-1[nm]", "hLn+hAl+1[nm]", "-1[nm]", "Wstack+1[nm]", "inside");
    box(model, "selLeftE", 2, "-1[nm]", "1[nm]", "-1[nm]", "hLn+1[nm]", "-1[nm]", "Wstack+1[nm]", "inside");
    box(model, "selRightE", 2, "p-1[nm]", "p+1[nm]", "-1[nm]", "hLn+1[nm]", "-1[nm]", "Wstack+1[nm]", "inside");
    model.component("comp1").selection().create("selPer", "Union");
    model.component("comp1").selection("selPer").set("entitydim", "2");
    model.component("comp1").selection("selPer").set("input", new String[]{"selLeft", "selRight"});
    model.component("comp1").selection().create("selPerE", "Union");
    model.component("comp1").selection("selPerE").set("entitydim", "2");
    model.component("comp1").selection("selPerE").set("input", new String[]{"selLeftE", "selRightE"});

    box(model, "selZ0", 2, "-1[nm]", "p+1[nm]", "-1[nm]", "hLn+hAl+1[nm]", "-1[nm]", "1[nm]", "inside");
    box(model, "selZ1", 2, "-1[nm]", "p+1[nm]", "-1[nm]", "hLn+hAl+1[nm]", "Lz-1[nm]", "Lz+1[nm]", "inside");
    box(model, "selZ0E", 2, "-1[nm]", "p+1[nm]", "-1[nm]", "hLn+1[nm]", "-1[nm]", "1[nm]", "inside");
    box(model, "selZ1E", 2, "-1[nm]", "p+1[nm]", "-1[nm]", "hLn+1[nm]", "Lz-1[nm]", "Lz+1[nm]", "inside");
    if (nSel(model, "selZ0") <= 0 || nSel(model, "selZ1") <= 0 || nSel(model, "selZ0E") <= 0 || nSel(model, "selZ1E") <= 0) {
      throw new RuntimeException("empty z selection");
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

    if (w0) {
      model.physics("solid").create("disp1", "Displacement3", 3);
      model.physics("solid").feature("disp1").selection().all();
      Object d = model.physics("solid").feature("disp1");
      setArr(d, "Direction", new String[]{"0", "0", "1"});
      setArr(d, "U0", new String[]{"0", "0", "0"});
      System.out.println("W0_READBACK Direction=" + Arrays.toString(getStrArr(d, "Direction"))
          + " U0=" + Arrays.toString(getStrArr(d, "U0"))
          + " nDom=" + model.physics("solid").feature("disp1").selection().entities().length);
    }

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
    try { nElem = model.mesh("mesh1").getNumElem(); } catch (Throwable t) { nElem = -1; }
    System.out.println("NUMELEM variant=" + variant + " n_elem=" + (nElem > 0 ? Integer.toString(nElem) : "NA"));

    model.study().create("stdE");
    model.study("stdE").create("eig", "Eigenfrequency");
    model.study("stdE").feature("eig").set("neigs", "24");
    model.study("stdE").feature("eig").set("shift", "3.0[GHz]");
    model.study("stdE").feature("eig").set("shiftactive", "on");
    model.study("stdE").createAutoSequences("all");
    System.out.println("BUILD_OK variant=" + variant);
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

  static boolean evalTensor(Model model, String expr, double[] out) {
    try {
      model.result().numerical().create("gt1", "EvalGlobal");
      model.result().numerical("gt1").set("expr", new String[]{"intLN(" + expr + ")/intLN(1)"});
      double[][] re = model.result().numerical("gt1").getReal();
      out[0] = re[0][0];
      System.out.println(String.format(Locale.US, "TENSOR expr=%s value=%.8e", expr, out[0]));
      try { model.result().numerical().remove("gt1"); } catch (Throwable t) {}
      return true;
    } catch (Throwable t) {
      System.out.println("TENSOR expr=" + expr + " value=UNDEFINED");
      try { model.result().numerical().remove("gt1"); } catch (Throwable t2) {}
      return false;
    }
  }

  static void checkTensor(Model model) {
    String[] names = new String[]{"solid.cEg22", "solid.cEg33", "solid.cEg15", "solid.cEg25", "solid.cEg46"};
    double[] expect = new double[]{2.029e11, 2.431e11, 9.0e9, -9.0e9, -8.99e9};
    boolean ok = true;
    for (int i = 0; i < names.length; i++) {
      double[] out = new double[]{Double.NaN};
      boolean def = evalTensor(model, names[i], out);
      boolean good = def && Math.abs(out[0] - expect[i]) <= 0.02 * Math.abs(expect[i]);
      System.out.println(String.format(Locale.US, "TENSOR_CHECK %s value=%.8e expect=%.8e ok=%s",
          names[i], out[0], expect[i], good));
      if (!good) ok = false;
    }
    if (!ok) throw new RuntimeException("tensor check failed");
  }

  static void solve(Model model, String variant) {
    model.study("stdE").run();
    checkTensor(model);
    model.result().numerical().create("gev1", "EvalGlobal");
    model.result().numerical("gev1").set("expr", new String[]{
      "freq", "intLN(solid.Ws)", "intAl(solid.Ws)",
      "intLN(u^2)", "intLN(v^2)", "intLN(w^2)"
    });
    model.result().numerical("gev1").set("looplevelinput", new String[]{"all"});
    double[][] re = model.result().numerical("gev1").getReal();
    double[][] im = model.result().numerical("gev1").getImag();
    int nMode = re[0].length;
    System.out.println("NMODE variant=" + variant + " n=" + nMode);
    for (int m = 0; m < nMode; m++) {
      double f = re[0][m];
      double fi = im[0][m];
      double eL = Math.abs(re[1][m]);
      double eA = Math.abs(re[2][m]);
      double u2 = Math.abs(re[3][m]);
      double v2 = Math.abs(re[4][m]);
      double w2 = Math.abs(re[5][m]);
      double et = eL + eA;
      double ut = u2 + v2 + w2;
      System.out.println(String.format(Locale.US,
          "ROW variant=%s dim=3 part=A f_GHz=%.6f fi_MHz=%.4f fracLN=%.4f fracAl=%.4f pu=%.3f pv=%.3f pw=%.3f orient=sys",
          variant, f / 1e9, fi / 1e6, et > 0 ? eL / et : -1, et > 0 ? eA / et : -1,
          ut > 0 ? u2 / ut : -1, ut > 0 ? v2 / ut : -1, ut > 0 ? w2 / ut : -1));
    }
  }
}
