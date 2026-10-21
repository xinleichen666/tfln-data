import com.comsol.model.*;
import com.comsol.model.util.*;
import java.lang.reflect.*;
import java.util.Arrays;
import java.util.Locale;

/**
 * Step 2 (p = 2.8326 um), 2D part.
 * Template: photoelastic_p283/scripts/Photo.java (eigenfrequency part only).
 * Variants: 2D-ref, 2D-noC, 2D-PS, 2D-OOP.
 */
public class Step2P283_2D {
  static final String PZ = "D:\\COMSOL63\\Multiphysics\\data\\comsol_piezo_lib.mph";
  static final String BASIC = "D:\\COMSOL63\\Multiphysics\\data\\comsol_basic_material_lib.mph";
  static boolean diagDone = false;

  public static void main(String[] args) {
    try {
      ModelUtil.initStandalone(true);
      System.out.println("STEP2_2D_START");
      runVariant("2D-ref", "ref");
      runVariant("2D-noC", "noC");
      runVariant("2D-PS", "PlaneStress");
      runVariant("2D-OOP", "OOP");
      System.out.println("STEP2_2D_DONE");
    } catch (Throwable t) {
      System.out.println("STEP2_2D_ABORT");
      t.printStackTrace(System.out);
    }
  }

  static void runVariant(String variant, String kind) {
    String tag = "M2" + variant.replace("-", "");
    System.out.println("VARIANT_BEGIN variant=" + variant + " dim=2 setting=" + kind);
    Model model = null;
    boolean ok = false;
    try {
      model = ModelUtil.create(tag);
      build(model, variant, kind);
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

  static String getStr(Object o, String name) {
    try { return (String) o.getClass().getMethod("getString", String.class).invoke(o, name); }
    catch (Throwable t) { return "ERR"; }
  }

  static String[] getStrArr(Object o, String name) {
    try { return (String[]) o.getClass().getMethod("getStringArray", String.class).invoke(o, name); }
    catch (Throwable t) { return new String[]{"ERR"}; }
  }

  static String[] allowed(Object o, String name) {
    try { return (String[]) o.getClass().getMethod("getAllowedPropertyValues", String.class).invoke(o, name); }
    catch (Throwable t) { return new String[]{"ERR"}; }
  }

  static Throwable unwrap(Throwable t) {
    if (t instanceof InvocationTargetException) return ((InvocationTargetException) t).getTargetException();
    return t;
  }

  static void printDiag(Model model) {
    Object p = model.physics("solid").prop("Type2D");
    System.out.println("DIAG_TYPE2D_GROUP " + p);
    String[] props = (String[]) call(p, "properties");
    System.out.println("DIAG_TYPE2D_PROPS " + Arrays.toString(props));
    for (int i = 0; i < props.length; i++) {
      System.out.println("DIAG_TYPE2D_VAL " + props[i] + " = " + getStr(p, props[i]));
    }
    System.out.println("DIAG_TYPE2D_ALLOWED = " + Arrays.toString(allowed(p, "Type2D")));
    Object f = model.physics("solid").field("displacement");
    Object comp = call(f, "component");
    String cs = "ERR";
    boolean hasW = false;
    if (comp instanceof String[]) {
      String[] arr = (String[]) comp;
      cs = Arrays.toString(arr);
      for (int i = 0; i < arr.length; i++) if (arr[i].equals("w")) hasW = true;
    }
    System.out.println("DIAG_DISP_COMPONENTS = " + cs);
    System.out.println("DIAG_DISP_HAS_W = " + hasW);
  }

  static void build(Model model, String variant, String kind) throws Exception {
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
    ln.set("basis", "on");
    ln.set("basisx", new String[]{"0", "1", "0"});
    ln.set("specifybasisy", "on");
    ln.set("basisy", new String[]{"-1", "0", "0"});
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

    model.physics("solid").feature("pzm1").create("dmp1", "Damping", 2);
    model.physics("solid").feature("pzm1").feature("dmp1").set("DampingType", "IsotropicLossFactor");
    model.physics("solid").feature("pzm1").feature("dmp1").set("eta_s_mat", "userdef");
    model.physics("solid").feature("pzm1").feature("dmp1").set("eta_s", "5e-4");

    if (!kind.equals("noC")) {
      model.physics("es").create("ccp1", "ChargeConservationPiezo", 2);
      model.physics("es").feature("ccp1").selection().named("selLN");
    } else {
      System.out.println("NO_CCP variant=" + variant);
    }

    model.physics("es").create("gndT", "Ground", 1);
    model.physics("es").feature("gndT").selection().named("selTerm");
    model.physics("es").create("gnd1", "Ground", 1);
    model.physics("es").feature("gnd1").selection().named("selGn");

    model.physics("solid").create("pc1", "PeriodicCondition", 1);
    model.physics("es").create("pc1", "PeriodicCondition", 1);
    applyPeriodic(model);

    if (!diagDone) {
      printDiag(model);
      diagDone = true;
    }

    Object prop = model.physics("solid").prop("Type2D");
    if (kind.equals("PlaneStress")) {
      prop.getClass().getMethod("set", String.class, String.class).invoke(prop, "Type2D", "PlaneStress");
    } else if (kind.equals("OOP")) {
      String[] av = allowed(prop, "Type2D");
      String found = null;
      for (int i = 0; i < av.length; i++) {
        String low = av[i].toLowerCase(Locale.US);
        if (low.contains("out") || low.contains("wave")) { found = av[i]; break; }
      }
      if (found == null) {
        System.out.println("DIAG_OOP_ALLOWED = " + Arrays.toString(av));
        throw new RuntimeException("no out-of-plane wave number option; allowed Type2D values = " + Arrays.toString(av));
      }
      prop.getClass().getMethod("set", String.class, String.class).invoke(prop, "Type2D", found);
    }
    System.out.println("TYPE2D_READBACK variant=" + variant + " value=" + getStr(prop, "Type2D"));

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
    int nl = 0;
    int nr = 0;
    double pmax = 0;
    for (int e = 1; e <= nE; e++) {
      double[][] a = model.geom("geom1").edgeX(e, new double[]{0.5});
      pmax = Math.max(pmax, a[0][0]);
    }
    for (int e = 1; e <= nE; e++) {
      double[][] a = model.geom("geom1").edgeX(e, new double[]{0.02, 0.98});
      double x0 = a[0][0];
      double y0 = a[0][1];
      double x1 = a[1][0];
      double y1 = a[1][1];
      if (Math.abs(x0 - x1) > 1e-10 || Math.abs(y0 - y1) < 1e-10) continue;
      double ylo = Math.min(y0, y1);
      double yhi = Math.max(y0, y1);
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
    System.out.println("VERT solid=" + sideEdges(model, false).length + " es=" + sideEdges(model, true).length);
  }

  static void solve(Model model, String variant) {
    model.study("stdE").run();
    model.result().numerical().create("gev1", "EvalGlobal");
    model.result().numerical("gev1").set("expr", new String[]{
      "freq", "intLN(solid.Ws)", "intAl(solid.Ws)", "intLN(u^2)", "intLN(v^2)"
    });
    model.result().numerical("gev1").set("looplevelinput", new String[]{"all"});
    double[][] re = model.result().numerical("gev1").getReal();
    double[][] im = model.result().numerical("gev1").getImag();
    boolean wExists = true;
    double[] w2arr = null;
    try {
      model.result().numerical().create("gevW", "EvalGlobal");
      model.result().numerical("gevW").set("expr", new String[]{"intLN(w^2)"});
      model.result().numerical("gevW").set("looplevelinput", new String[]{"all"});
      w2arr = model.result().numerical("gevW").getReal()[0];
      System.out.println("W_EXISTS variant=" + variant + " nW=" + w2arr.length);
    } catch (Throwable tex) {
      wExists = false;
      System.out.println("W_UNDEFINED variant=" + variant);
    }
    int nMode = re[0].length;
    System.out.println("NMODE variant=" + variant + " n=" + nMode);
    for (int m = 0; m < nMode; m++) {
      double f = re[0][m];
      double fi = im[0][m];
      double eL = Math.abs(re[1][m]);
      double eA = Math.abs(re[2][m]);
      double u2 = Math.abs(re[3][m]);
      double v2 = Math.abs(re[4][m]);
      double et = eL + eA;
      double w2 = wExists ? Math.abs(w2arr[m]) : 0.0;
      double ut = wExists ? (u2 + v2 + w2) : (u2 + v2);
      String pw = wExists ? String.format(Locale.US, "%.3f", ut > 0 ? w2 / ut : -1) : "NaN";
      System.out.println(String.format(Locale.US,
          "ROW variant=%s dim=2 f_GHz=%.6f fi_MHz=%.4f fracLN=%.4f fracAl=%.4f pu=%.3f pv=%.3f pw=%s",
          variant, f / 1e9, fi / 1e6, et > 0 ? eL / et : -1, et > 0 ? eA / et : -1,
          ut > 0 ? u2 / ut : -1, ut > 0 ? v2 / ut : -1, pw));
    }
  }
}
