import com.comsol.model.*;
import com.comsol.model.util.*;
import java.lang.reflect.*;
import java.util.Arrays;
import java.util.Locale;

/**
 * Step 3, 2D part: material orientation / tensor consistency.
 * Template: step2_p283_check/Step2P283_2D.java
 */
public class Step3Orient2D {
  static final String PZ = "D:\\COMSOL63\\Multiphysics\\data\\comsol_piezo_lib.mph";
  static final String BASIC = "D:\\COMSOL63\\Multiphysics\\data\\comsol_basic_material_lib.mph";
  static final String[] PRIMARY = new String[]{
    "solid.cE11","solid.cE22","solid.cE33","solid.cE12","solid.cE13","solid.cE23",
    "solid.cE44","solid.cE55","solid.cE66","solid.cE14","solid.cE15","solid.cE16",
    "solid.cE24","solid.cE25","solid.cE26","solid.cE34","solid.cE35","solid.cE36",
    "solid.cE45","solid.cE46","solid.cE56",
    "solid.eES11","solid.eES12","solid.eES13","solid.eES14","solid.eES15","solid.eES16",
    "solid.eES21","solid.eES22","solid.eES23","solid.eES24","solid.eES25","solid.eES26",
    "solid.eES31","solid.eES32","solid.eES33","solid.eES34","solid.eES35","solid.eES36",
    "solid.D11","solid.D22","solid.D33","solid.D12","solid.D44","solid.D55","solid.D66",
    "solid.cEg11","solid.cEg22","solid.cEg33","solid.cEg12","solid.cEg13","solid.cEg23",
    "solid.cEg44","solid.cEg55","solid.cEg66","solid.cEg14","solid.cEg15","solid.cEg16",
    "solid.cEg24","solid.cEg25","solid.cEg26","solid.cEg34","solid.cEg35","solid.cEg36",
    "solid.cEg45","solid.cEg46","solid.cEg56"
  };
  static final String[] ALT = new String[]{
    "solid.eESg11","solid.eESg12","solid.eESg21","solid.eESg31",
    "solid.dETg11","solid.epsilonrSg11","solid.Dg11"
  };

  public static void main(String[] args) {
    try {
      ModelUtil.initStandalone(true);
      System.out.println("STEP3_2D_START");
      runVariant("2D-basis", "basis", "40/NA", false, false);
      runVariant("2D-basisFine", "basis", "20/4", true, false);
      runVariant("2D-sys", "sys", "40/NA", false, false);
      runVariant("2D-norot", "norot", "40/NA", false, false);
      runVariant("2D-basisME", "basis", "40/NA", false, true);
      runVariant("2D-sysME", "sys", "40/NA", false, true);
      System.out.println("STEP3_2D_DONE");
    } catch (Throwable t) {
      System.out.println("STEP3_2D_ABORT");
      t.printStackTrace(System.out);
    }
  }

  static void runVariant(String variant, String orient, String mesh, boolean fine, boolean me) {
    String tag = "M3" + variant.replace("-", "");
    System.out.println("VARIANT_BEGIN variant=" + variant + " dim=2 setting=" + orient
        + (fine ? ";fineMesh" : "") + (me ? ";ModeExtension" : "") + " orient=" + orient);
    Model model = null;
    boolean ok = false;
    try {
      model = ModelUtil.create(tag);
      build(model, variant, orient, fine, me);
      solve(model, variant, orient);
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
    if (s.length() > 240) s = s.substring(0, 240);
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

  static void box(Model model, String tag, int dim, String xmin, String xmax, String ymin, String ymax) {
    model.component("comp1").selection().create(tag, "Box");
    model.component("comp1").selection(tag).set("entitydim", Integer.toString(dim));
    model.component("comp1").selection(tag).set("condition", "intersects");
    model.component("comp1").selection(tag).set("xmin", xmin);
    model.component("comp1").selection(tag).set("xmax", xmax);
    model.component("comp1").selection(tag).set("ymin", ymin);
    model.component("comp1").selection(tag).set("ymax", ymax);
  }

  static Object call(Object o, String meth) {
    try { return o.getClass().getMethod(meth).invoke(o); }
    catch (Throwable t) { return "ERR:" + oneLine(unwrap(t)); }
  }
  static Object call(Object o, String meth, String arg) {
    try { return o.getClass().getMethod(meth, String.class).invoke(o, arg); }
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
  static String[] allowed(Object o, String n) {
    try { return (String[]) o.getClass().getMethod("getAllowedPropertyValues", String.class).invoke(o, n); }
    catch (Throwable t) { return new String[]{"-"}; }
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

  static void printGroup(String label, Object o) {
    String[] props = (String[]) call(o, "properties");
    System.out.println("DIAG_" + label + "_PROPS = " + Arrays.toString(props));
    for (int i = 0; i < props.length; i++) {
      String v = getStr(o, props[i]);
      if (v.equals("ERR")) {
        try { v = Arrays.toString((String[]) o.getClass().getMethod("getStringArray", String.class).invoke(o, props[i])); } catch (Throwable t) {}
      }
      if (props[i].toLowerCase().contains("coord")) {
        System.out.println("DIAG_" + label + "_VAL " + props[i] + " = " + v);
      }
    }
  }

  static void setupOrient(Model model, String orient, String variant) throws Exception {
    if (orient.equals("sys")) {
      Object sys = model.component("comp1").coordSystem().create("sys2", "Rotated");
      System.out.println("SYS2 " + sys);
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
      setStr(pz, "coordinateSystem", "sys2");
      setStr(cc, "coordinateSystem", "sys2");
      System.out.println("COORD_SYS_SET variant=" + variant + " pzm1=" + getStr(pz, "coordinateSystem")
          + " ccp1=" + getStr(cc,  "coordinateSystem"));
    } else if (orient.equals("norot")) {
      Object pz = model.physics("solid").feature("pzm1");
      Object cc = model.physics("es").feature("ccp1");
      System.out.println("NOROT_DEFAULT_COORD pzm1=" + getStr(pz, "coordinateSystem")
          + " ccp1=" + getStr(cc, "coordinateSystem"));
      setStr(pz, "coordinateSystem", "GlobalSystem");
      setStr(cc, "coordinateSystem", "GlobalSystem");
      System.out.println("COORD_SYS_SET variant=" + variant + " pzm1=" + getStr(pz, "coordinateSystem")
          + " ccp1=" + getStr(cc, "coordinateSystem"));
    } else {
      Object pz = model.physics("solid").feature("pzm1");
      Object cc = model.physics("es").feature("ccp1");
      System.out.println("BASIS_DEFAULT_COORD pzm1=" + getStr(pz, "coordinateSystem")
          + " ccp1=" + getStr(cc, "coordinateSystem"));
    }
  }

  static void build(Model model, String variant, String orient, boolean fine, boolean me) throws Exception {
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

    box(model, "selLN", 2, "1[nm]", "p-1[nm]", "1[nm]", "hLn-1[nm]");
    box(model, "selAl", 2, "1[nm]", "p-1[nm]", "hLn+1[nm]", "hLn+hAl-1[nm]");
    box(model, "selTerm", 1, "(p-2*duty*p)/4-1[nm]", "(p-2*duty*p)/4+duty*p+1[nm]", "hLn-1[nm]", "hLn+1[nm]");
    box(model, "selGn", 1, "p/2+(p-2*duty*p)/4-1[nm]", "p/2+(p-2*duty*p)/4+duty*p+1[nm]", "hLn-1[nm]", "hLn+1[nm]");

    Model pz = ModelUtil.load("pz", PZ);
    Model basic = ModelUtil.load("basic", BASIC);
    Material ln = model.component("comp1").material().create("matLN", "Common");
    ln.selection().named("selLN");
    if (orient.equals("basis")) {
      ln.set("basis", "on");
      ln.set("basisx", new String[]{"0", "1", "0"});
      ln.set("specifybasisy", "on");
      ln.set("basisy", new String[]{"-1", "0", "0"});
    }
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

    setupOrient(model, orient, variant);

    model.physics("solid").feature("pzm1").create("dmp1", "Damping", 2);
    model.physics("solid").feature("pzm1").feature("dmp1").set("DampingType", "IsotropicLossFactor");
    model.physics("solid").feature("pzm1").feature("dmp1").set("eta_s_mat", "userdef");
    model.physics("solid").feature("pzm1").feature("dmp1").set("eta_s", "5e-4");

    model.physics("es").create("gndT", "Ground", 1);
    model.physics("es").feature("gndT").selection().named("selTerm");
    model.physics("es").create("gnd1", "Ground", 1);
    model.physics("es").feature("gnd1").selection().named("selGn");

    model.physics("solid").create("pc1", "PeriodicCondition", 1);
    model.physics("es").create("pc1", "PeriodicCondition", 1);
    applyPeriodic(model);

    if (me) {
      Object prop = model.physics("solid").prop("Type2D");
      setStr(prop, "ModeExtension", "1");
      setStr(prop, "kz", "0");
      System.out.println("TYPE2D_ME variant=" + variant
          + " ModeExtension=" + getStr(prop, "ModeExtension")
          + " kz=" + getStr(prop, "kz")
          + " Type2D=" + getStr(prop, "Type2D"));
    }
    System.out.println("TYPE2D_READBACK variant=" + variant + " value="
        + getStr(model.physics("solid").prop("Type2D"), "Type2D"));

    model.component("comp1").cpl().create("intLN", "Integration");
    model.component("comp1").cpl("intLN").selection().geom("geom1", 2);
    model.component("comp1").cpl("intLN").selection().named("selLN");
    model.component("comp1").cpl().create("intAl", "Integration");
    model.component("comp1").cpl("intAl").selection().geom("geom1", 2);
    model.component("comp1").cpl("intAl").selection().named("selAl");

    model.mesh().create("mesh1", "geom1");
    if (fine) {
      addSize(model, "szLN", "selLN", "20[nm]", "4[nm]");
      addSize(model, "szAl", "selAl", "20[nm]", "4[nm]");
    } else {
      model.mesh("mesh1").feature().create("szLN", "Size");
      model.mesh("mesh1").feature("szLN").selection().geom("geom1", 2);
      model.mesh("mesh1").feature("szLN").selection().named("selLN");
      model.mesh("mesh1").feature("szLN").set("hmaxactive", "on");
      model.mesh("mesh1").feature("szLN").set("hmax", "40[nm]");
    }
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

  static void addSize(Model model, String tag, String sel, String hmax, String hmin) {
    model.mesh("mesh1").feature().create(tag, "Size");
    model.mesh("mesh1").feature(tag).selection().geom("geom1", 2);
    model.mesh("mesh1").feature(tag).selection().named(sel);
    model.mesh("mesh1").feature(tag).set("hmaxactive", "on");
    model.mesh("mesh1").feature(tag).set("hminactive", "on");
    model.mesh("mesh1").feature(tag).set("hmax", hmax);
    model.mesh("mesh1").feature(tag).set("hmin", hmin);
  }

  static int[] sideEdges(Model model, boolean lnOnly) {
    int nE = model.geom("geom1").getNEdges();
    int[] left = new int[nE];
    int[] right = new int[nE];
    int nl = 0;
    int nr = 0;
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

  static void solve(Model model, String variant, String orient) {
    model.study("stdE").run();
    double[][] re;
    double[][] im;
    boolean wExists = true;
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
          "ROW variant=%s dim=2 f_GHz=%.6f fi_MHz=%.4f fracLN=%.4f fracAl=%.4f pu=%.3f pv=%.3f pw=%s orient=%s",
          variant, f / 1e9, fi / 1e6, et > 0 ? eL / et : -1, et > 0 ? eA / et : -1,
          ut > 0 ? u2 / ut : -1, ut > 0 ? v2 / ut : -1, pw, orient));
    }
    // tensor diagnostics
    int nDefined = 0;
    for (int i = 0; i < PRIMARY.length; i++) {
      boolean ok = evalTensor(model, variant, orient, PRIMARY[i]);
      if (ok) nDefined++;
    }
    System.out.println("TENSOR_DEFINED_COUNT variant=" + variant + " n=" + nDefined + "/" + PRIMARY.length);
    if (true) {
      for (int i = 0; i < ALT.length; i++) {
        if (evalTensor(model, variant + "_ALT", orient, ALT[i])) {
          System.out.println("TENSOR_ALT_DEFINED variant=" + variant + " expr=" + ALT[i]);
        }
      }
    }
  }

  static boolean evalTensor(Model model, String variant, String orient, String expr) {
    try {
      model.result().numerical().create("gt1", "EvalGlobal");
      model.result().numerical("gt1").set("expr", new String[]{"intLN(" + expr + ")/intLN(1)"});
      double[][] re = model.result().numerical("gt1").getReal();
      System.out.println(String.format(Locale.US, "TENSOR variant=%s orient=%s expr=%s value=%.8e",
          variant, orient, expr, re[0][0]));
      try { model.result().numerical().remove("gt1"); } catch (Throwable t) {}
      return true;
    } catch (Throwable t) {
      System.out.println("TENSOR variant=" + variant + " orient=" + orient + " expr=" + expr + " value=UNDEFINED");
      try { model.result().numerical().remove("gt1"); } catch (Throwable t2) {}
      return false;
    }
  }
}
