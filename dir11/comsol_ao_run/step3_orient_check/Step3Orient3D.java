import com.comsol.model.*;
import com.comsol.model.util.*;
import java.lang.reflect.*;
import java.util.Arrays;
import java.util.Locale;

/**
 * Step 3, 3D part: material orientation / tensor consistency (z-periodic slice).
 * Template: step2_p283_check/Step2P283_3D.java
 */
public class Step3Orient3D {
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
      System.out.println("STEP3_3D_START");
      runVariant("3D-W0-basis", "basis", true);
      runVariant("3D-W0-sys", "sys", true);
      runVariant("3D-W0-norot", "norot", true);
      runVariant("3D-D-sys", "sys", false);
      System.out.println("STEP3_3D_DONE");
    } catch (Throwable t) {
      System.out.println("STEP3_3D_ABORT");
      t.printStackTrace(System.out);
    }
  }

  static void runVariant(String variant, String orient, boolean w0) {
    String tag = "M3D" + variant.replace("-", "");
    System.out.println("VARIANT_BEGIN variant=" + variant + " dim=3 setting=" + orient
        + (w0 ? ";prescribedZ0" : ";noW0") + " orient=" + orient);
    Model model = null;
    boolean ok = false;
    try {
      model = ModelUtil.create(tag);
      build(model, variant, orient, w0);
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
    try { return model.component("comp1").selection(tag).entities().length; }
    catch (Throwable t) { return -1; }
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
  static String arr2s(String[] a) {
    StringBuilder b = new StringBuilder("[");
    for (int i = 0; i < a.length; i++) { if (i > 0) b.append(";"); b.append(a[i]); }
    return b.append("]").toString();
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
      System.out.println("SYS2_SET angle=" + getStr(sys, "angle") + " seq=" + getStr(sys, "rotationSequence")
          + " frametype=" + getStr(sys, "frametype"));
      Object pz = model.physics("solid").feature("pzm1");
      Object cc = model.physics("es").feature("ccp1");
      setStr(pz, "coordinateSystem", "sys2");
      setStr(cc, "coordinateSystem", "sys2");
      System.out.println("COORD_SYS_SET variant=" + variant + " pzm1=" + getStr(pz, "coordinateSystem")
          + " ccp1=" + getStr(cc, "coordinateSystem"));
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

  static void build(Model model, String variant, String orient, boolean w0) throws Exception {
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
    if (orient.equals("basis")) {
      ln.set("basis", "on");
      ln.set("basisx", new String[]{"0", "1", "0"});
      ln.set("specifybasisy", "on");
      ln.set("basisy", new String[]{"-1", "0", "0"});
    }
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
    model.physics("es").create("ccp1", "ChargeConservationPiezo", 3);
    model.physics("es").feature("ccp1").selection().named("selLN");

    setupOrient(model, orient, variant);

    model.physics("solid").feature("pzm1").create("dmp1", "Damping", 3);
    model.physics("solid").feature("pzm1").feature("dmp1").set("DampingType", "IsotropicLossFactor");
    model.physics("solid").feature("pzm1").feature("dmp1").set("eta_s_mat", "userdef");
    model.physics("solid").feature("pzm1").feature("dmp1").set("eta_s", "5e-4");
    try {
      model.physics("solid").prop("ShapeProperty").set("order_displacement", "2");
    } catch (Throwable ex) {
      System.out.println("ORDER_SET_FAIL variant=" + variant + " reason=" + oneLine(ex));
    }
    System.out.println("ORDER_READBACK variant=" + variant + " order=2 read="
        + getStr(model.physics("solid").prop("ShapeProperty"), "order_displacement"));

    model.physics("es").create("gnd1", "Ground", 2);
    model.physics("es").feature("gnd1").selection().named("selGnd");

    box(model, "selLeft", 2, "-1[nm]", "1[nm]", "-1[nm]", "hLn+hAl+1[nm]", "-1[nm]", "Wstack+1[nm]");
    box(model, "selRight", 2, "p-1[nm]", "p+1[nm]", "-1[nm]", "hLn+hAl+1[nm]", "-1[nm]", "Wstack+1[nm]");
    box(model, "selLeftE", 2, "-1[nm]", "1[nm]", "-1[nm]", "hLn+1[nm]", "-1[nm]", "Wstack+1[nm]");
    box(model, "selRightE", 2, "p-1[nm]", "p+1[nm]", "-1[nm]", "hLn+1[nm]", "-1[nm]", "Wstack+1[nm]");
    model.component("comp1").selection("selLeft").set("condition", "inside");
    model.component("comp1").selection("selRight").set("condition", "inside");
    model.component("comp1").selection("selLeftE").set("condition", "inside");
    model.component("comp1").selection("selRightE").set("condition", "inside");
    model.component("comp1").selection().create("selPer", "Union");
    model.component("comp1").selection("selPer").set("entitydim", "2");
    model.component("comp1").selection("selPer").set("input", new String[]{"selLeft", "selRight"});
    model.component("comp1").selection().create("selPerE", "Union");
    model.component("comp1").selection("selPerE").set("entitydim", "2");
    model.component("comp1").selection("selPerE").set("input", new String[]{"selLeftE", "selRightE"});

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
      System.out.println("W0_READBACK variant=" + variant
          + " Direction=" + arr2s(getStrArr(d, "Direction"))
          + " U0=" + arr2s(getStrArr(d, "U0"))
          + " nDom=" + model.physics("solid").feature("disp1").selection().entities().length);
    }

    model.component("comp1").cpl().create("intLN", "Integration");
    model.component("comp1").cpl("intLN").selection().geom("geom1", 3);
    model.component("comp1").cpl("intLN").selection().named("selLN");
    model.component("comp1").cpl().create("intAl", "Integration");
    model.component("comp1").cpl("intAl").selection().geom("geom1", 3);
    model.component("comp1").cpl("intAl").selection().named("selAl");

    model.mesh().create("mesh1", "geom1");
    size(model, "szLN", "selLN", "75[nm]", "20[nm]");
    size(model, "szAl", "selAl", "40[nm]", "10[nm]");
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

  static void solve(Model model, String variant, String orient) {
    model.study("stdE").run();
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
          "ROW variant=%s dim=3 f_GHz=%.6f fi_MHz=%.4f fracLN=%.4f fracAl=%.4f pu=%.3f pv=%.3f pw=%.3f orient=%s",
          variant, f / 1e9, fi / 1e6, et > 0 ? eL / et : -1, et > 0 ? eA / et : -1,
          ut > 0 ? u2 / ut : -1, ut > 0 ? v2 / ut : -1, ut > 0 ? w2 / ut : -1, orient));
    }
    int nDefined = 0;
    for (int i = 0; i < PRIMARY.length; i++) {
      if (evalTensor(model, variant, orient, PRIMARY[i])) nDefined++;
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
