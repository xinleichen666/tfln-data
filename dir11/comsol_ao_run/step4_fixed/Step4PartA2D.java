import com.comsol.model.*;
import com.comsol.model.util.*;
import java.lang.reflect.*;
import java.util.Arrays;
import java.util.Locale;

/** Step 4 Part A, 2D: fixed orientation (sys2) and ground selection (inside). */
public class Step4PartA2D {
  static final String PZ = "D:\\COMSOL63\\Multiphysics\\data\\comsol_piezo_lib.mph";
  static final String BASIC = "D:\\COMSOL63\\Multiphysics\\data\\comsol_basic_material_lib.mph";

  public static void main(String[] args) {
    try {
      ModelUtil.initStandalone(true);
      System.out.println("STEP4_2D_START");
      runVariant("2D-A", false, false);
      runVariant("2D-B", true, false);
      runVariant("2D-B-oldgnd", true, true);
      System.out.println("STEP4_2D_DONE");
    } catch (Throwable t) {
      System.out.println("STEP4_2D_ABORT");
      t.printStackTrace(System.out);
    }
  }

  static void runVariant(String variant, boolean me, boolean oldGnd) {
    String tag = "M4" + variant.replace("-", "");
    System.out.println("VARIANT_BEGIN variant=" + variant + " dim=2 part=A setting=" + (me ? "ModeExtension" : "PlaneStrain")
        + (oldGnd ? ";oldgnd" : "") + " orient=sys");
    Model model = null;
    boolean ok = false;
    try {
      model = ModelUtil.create(tag);
      build(model, variant, me, oldGnd);
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
    String s = ex.getClass().getSimpleName() + ": " + String.valueOf(ex.getMessage());
    s = s.replace('\n', ' ').replace('\r', ' ').replace(',', ';');
    if (s.length() > 260) s = s.substring(0, 260);
    return s;
  }

  static void copyGroup(Material dst, Material src, String group, boolean create) {
    if (create) dst.propertyGroup().create(group, group);
    String[] names = src.propertyGroup(group).properties();
    for (int i = 0; i < names.length; i++) {
      try {
        dst.propertyGroup(group).set(names[i], src.propertyGroup(group).getStringArray(names[i]));
      } catch (Exception ex) { System.out.println("skip " + group + "." + names[i]); }
    }
  }

  static void box(Model model, String tag, int dim, String xmin, String xmax, String ymin, String ymax, String cond) {
    model.component("comp1").selection().create(tag, "Box");
    model.component("comp1").selection(tag).set("entitydim", Integer.toString(dim));
    model.component("comp1").selection(tag).set("condition", cond);
    model.component("comp1").selection(tag).set("xmin", xmin);
    model.component("comp1").selection(tag).set("xmax", xmax);
    model.component("comp1").selection(tag).set("ymin", ymin);
    model.component("comp1").selection(tag).set("ymax", ymax);
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

  static void checkGround(Model model, String tag, String variant) throws Exception {
    int[] ents = model.component("comp1").selection(tag).entities();
    System.out.println("GROUND_CHECK variant=" + variant + " tag=" + tag + " n=" + ents.length);
    for (int i = 0; i < ents.length; i++) {
      double[][] xy = model.geom("geom1").edgeX(ents[i], new double[]{0, 1});
      StringBuilder sb = new StringBuilder();
      for (int k = 0; k < xy.length; k++) {
        sb.append(String.format(Locale.US, " (% .6e,% .6e)", xy[k][0], xy[k][1]));
      }
      System.out.println("GROUND_EDGE variant=" + variant + " tag=" + tag + " id=" + ents[i] + " pts=" + sb);
    }
  }

  static void build(Model model, String variant, boolean me, boolean oldGnd) throws Exception {
    model.param().set("p", "2.8326[um]");
    model.param().set("hLn", "500[nm]");
    model.param().set("hAl", "100[nm]");
    model.param().set("duty", "0.25");

    model.modelNode().create("comp1");
    model.geom().create("geom1", 2);
    model.geom("geom1").lengthUnit("m");
    model.geom("geom1").feature().create("rLn", "Rectangle");
    model.geom("geom1").feature("rLn").set("size", new String[]{"p", "hLn"});
    model.geom("geom1").feature("rLn").set("pos", new String[]{"0", "0"});
    model.geom("geom1").feature().create("rAp", "Rectangle");
    model.geom("geom1").feature("rAp").set("size", new String[]{"duty*p", "hAl"});
    model.geom("geom1").feature("rAp").set("pos", new String[]{"(p-2*duty*p)/4", "hLn"});
    model.geom("geom1").feature().create("rAn", "Rectangle");
    model.geom("geom1").feature("rAn").set("size", new String[]{"duty*p", "hAl"});
    model.geom("geom1").feature("rAn").set("pos", new String[]{"p/2+(p-2*duty*p)/4", "hLn"});
    model.geom("geom1").run();

    String cond = oldGnd ? "intersects" : "inside";
    box(model, "selLN", 2, "1[nm]", "p-1[nm]", "1[nm]", "hLn-1[nm]", "intersects");
    box(model, "selAl", 2, "1[nm]", "p-1[nm]", "hLn+1[nm]", "hLn+hAl-1[nm]", "intersects");
    box(model, "selTerm", 1, "(p-2*duty*p)/4-1[nm]", "(p-2*duty*p)/4+duty*p+1[nm]", "hLn-1[nm]", "hLn+1[nm]", cond);
    box(model, "selGn", 1, "p/2+(p-2*duty*p)/4-1[nm]", "p/2+(p-2*duty*p)/4+duty*p+1[nm]", "hLn-1[nm]", "hLn+1[nm]", cond);

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
    model.physics("solid").create("pzm1", "PiezoelectricMaterialModel", 2);
    model.physics("solid").feature("pzm1").selection().named("selLN");
    model.multiphysics().create("pze1", "PiezoelectricEffect", "geom1");
    model.physics("es").create("ccp1", "ChargeConservationPiezo", 2);
    model.physics("es").feature("ccp1").selection().named("selLN");
    setupSys(model);

    model.physics("solid").feature("pzm1").create("dmp1", "Damping", 2);
    model.physics("solid").feature("pzm1").feature("dmp1").set("DampingType", "IsotropicLossFactor");
    model.physics("solid").feature("pzm1").feature("dmp1").set("eta_s_mat", "userdef");
    model.physics("solid").feature("pzm1").feature("dmp1").set("eta_s", "5e-4");

    model.physics("es").create("gndT", "Ground", 1);
    model.physics("es").feature("gndT").selection().named("selTerm");
    model.physics("es").create("gnd1", "Ground", 1);
    model.physics("es").feature("gnd1").selection().named("selGn");
    checkGround(model, "selTerm", variant);
    checkGround(model, "selGn", variant);
    if (!oldGnd) {
      int nt = model.component("comp1").selection("selTerm").entities().length;
      int ng = model.component("comp1").selection("selGn").entities().length;
      if (nt != 1 || ng != 1) {
        throw new RuntimeException("ground check failed: selTerm=" + nt + ", selGn=" + ng);
      }
    }

    model.physics("solid").create("pc1", "PeriodicCondition", 1);
    model.physics("es").create("pc1", "PeriodicCondition", 1);
    applyPeriodic(model);

    if (me) {
      Object prop = model.physics("solid").prop("Type2D");
      setStr(prop, "ModeExtension", "1");
      setStr(prop, "kz", "0");
      System.out.println("TYPE2D_ME ModeExtension=" + getStr(prop, "ModeExtension") + " kz=" + getStr(prop, "kz")
          + " Type2D=" + getStr(prop, "Type2D"));
    }
    System.out.println("TYPE2D_READBACK Type2D=" + getStr(model.physics("solid").prop("Type2D"), "Type2D")
        + " ModeExtension=" + getStr(model.physics("solid").prop("Type2D"), "ModeExtension")
        + " kz=" + getStr(model.physics("solid").prop("Type2D"), "kz"));

    model.component("comp1").cpl().create("intLN", "Integration");
    model.component("comp1").cpl("intLN").selection().geom("geom1", 2);
    model.component("comp1").cpl("intLN").selection().named("selLN");
    model.component("comp1").cpl().create("intAl", "Integration");
    model.component("comp1").cpl("intAl").selection().geom("geom1", 2);
    model.component("comp1").cpl("intAl").selection().named("selAl");

    model.mesh().create("mesh1", "geom1");
    model.mesh("mesh1").feature().create("szLN", "Size");
    model.mesh("mesh1").feature("szLN").selection().geom("geom1", 2);
    model.mesh("mesh1").feature("szLN").selection().named("selLN");
    model.mesh("mesh1").feature("szLN").set("hmaxactive", "on");
    model.mesh("mesh1").feature("szLN").set("hmax", "40[nm]");
    model.mesh("mesh1").feature().create("ftri1", "FreeTri");
    model.mesh("mesh1").feature("ftri1").selection().geom("geom1", 2);
    model.mesh("mesh1").feature("ftri1").selection().all();
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

  static int[] sideEdges(Model model, boolean lnOnly) {
    int nE = model.geom("geom1").getNEdges();
    int[] left = new int[nE];
    int[] right = new int[nE];
    int nl = 0, nr = 0;
    double pmax = 0;
    for (int e = 1; e <= nE; e++) {
      double[][] a = model.geom("geom1").edgeX(e, new double[]{0.5});
      pmax = Math.max(pmax, a[0][0]);
    }
    for (int e = 1; e <= nE; e++) {
      double[][] a = model.geom("geom1").edgeX(e, new double[]{0.02, 0.98});
      double x0 = a[0][0], y0 = a[0][1], x1 = a[1][0], y1 = a[1][1];
      if (Math.abs(x0 - x1) > 1e-10 || Math.abs(y0 - y1) < 1e-10) continue;
      double ylo = Math.min(y0, y1), yhi = Math.max(y0, y1);
      if (lnOnly && (ylo < -1e-9 || yhi > 500e-9 + 1e-9)) continue;
      if (Math.abs(x0) < 1e-9) left[nl++] = e;
      if (Math.abs(x0 - pmax) < 1e-9) right[nr++] = e;
    }
    int[] use = new int[nl + nr];
    System.arraycopy(left, 0, use, 0, nl);
    System.arraycopy(right, 0, use, nl, nr);
    return use;
  }

  static void applyPeriodic(Model model) {
    model.physics("solid").feature("pc1").selection().set(sideEdges(model, false));
    model.physics("es").feature("pc1").selection().set(sideEdges(model, true));
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
    boolean wExists = true;
    double[][] re, im;
    try {
      model.result().numerical().create("gev1", "EvalGlobal");
      model.result().numerical("gev1").set("expr", new String[]{
        "freq", "intLN(solid.Ws)", "intAl(solid.Ws)", "intLN(u^2)", "intLN(v^2)", "intLN(w^2)"
      });
      model.result().numerical("gev1").set("looplevelinput", new String[]{"all"});
      re = model.result().numerical("gev1").getReal();
      im = model.result().numerical("gev1").getImag();
    } catch (Throwable t1) {
      wExists = false;
      try { model.result().numerical().remove("gev1"); } catch (Throwable t2) {}
      model.result().numerical().create("gev1", "EvalGlobal");
      model.result().numerical("gev1").set("expr", new String[]{
        "freq", "intLN(solid.Ws)", "intAl(solid.Ws)", "intLN(u^2)", "intLN(v^2)"
      });
      model.result().numerical("gev1").set("looplevelinput", new String[]{"all"});
      re = model.result().numerical("gev1").getReal();
      im = model.result().numerical("gev1").getImag();
    }
    System.out.println(wExists ? ("W_EXISTS variant=" + variant) : ("W_UNDEFINED variant=" + variant));
    int nMode = re[0].length;
    System.out.println("NMODE variant=" + variant + " n=" + nMode);
    for (int m = 0; m < nMode; m++) {
      double f = re[0][m];
      double fi = im[0][m];
      double eL = Math.abs(re[1][m]);
      double eA = Math.abs(re[2][m]);
      double u2 = Math.abs(re[3][m]);
      double v2 = Math.abs(re[4][m]);
      double w2 = wExists ? Math.abs(re[5][m]) : 0.0;
      double et = eL + eA;
      double ut = wExists ? (u2 + v2 + w2) : (u2 + v2);
      String pw = wExists ? String.format(Locale.US, "%.3f", ut > 0 ? w2 / ut : -1) : "NaN";
      System.out.println(String.format(Locale.US,
          "ROW variant=%s dim=2 part=A f_GHz=%.6f fi_MHz=%.4f fracLN=%.4f fracAl=%.4f pu=%.3f pv=%.3f pw=%s orient=sys",
          variant, f / 1e9, fi / 1e6, et > 0 ? eL / et : -1, et > 0 ? eA / et : -1,
          ut > 0 ? u2 / ut : -1, ut > 0 ? v2 / ut : -1, pw));
    }
  }
}
