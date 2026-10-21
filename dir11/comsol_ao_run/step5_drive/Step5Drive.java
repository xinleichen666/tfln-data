import com.comsol.model.*;
import com.comsol.model.util.*;
import java.lang.reflect.*;
import java.util.*;
import java.util.Locale;

/** Step 5: 1 V frequency-domain drive at p_new; photoelastic + EO + moving-boundary dn metrics. */
public class Step5Drive {
  static final String PZ = "D:\\COMSOL63\\Multiphysics\\data\\comsol_piezo_lib.mph";
  static final String BASIC = "D:\\COMSOL63\\Multiphysics\\data\\comsol_basic_material_lib.mph";
  static final double P_UM = 2.8526131500;
  static final double NE = 2.138;
  static final double NEFF = 1.88978;
  static final double KAPPA = 4.052926e6;
  static final double P31 = 0.179;
  static final double P33 = 0.071;
  static final double R13 = 8.6e-12;
  static final double R33 = 30.8e-12;
  static final int NH = 16;
  static final int NWIN = 48;

  public static void main(String[] args) {
    try {
      ModelUtil.initStandalone(true);
      System.out.println("STEP5_START");
      Model model = ModelUtil.create("M5");
      build(model);
      double[] eig = runEigen(model);
      double fT = eig[0], fP = eig[1];
      System.out.println(String.format(Locale.US, "EIG_USED f_target_GHz=%.9f f_partner_GHz=%.9f", fT, fP));
      // switch to 1 V drive
      model.physics("es").feature().remove("gndT");
      model.physics("es").create("term1", "Terminal", 1);
      model.physics("es").feature("term1").selection().named("selTerm");
      model.physics("es").feature("term1").set("TerminalType", "Voltage");
      model.physics("es").feature("term1").set("V0", "1[V]");
      int nt = model.component("comp1").selection("selTerm").entities().length;
      int ng = model.component("comp1").selection("selGn").entities().length;
      System.out.println("TERMINAL_CHECK nTerm=" + nt + " nGround=" + ng + " termTag=term1");
      if (nt != 1 || ng != 1) throw new RuntimeException("terminal/ground entity check failed");
      // frequency list
      TreeSet<Double> setF = new TreeSet<Double>();
      for (int i = 0; i <= 80; i++) setF.add(3.30 + 0.001 * i);
      for (int i = -40; i <= 40; i++) setF.add(fT + 0.00005 * i);
      for (int i = -40; i <= 40; i++) setF.add(fP + 0.00005 * i);
      StringBuilder pl = new StringBuilder();
      for (Double f : setF) {
        if (pl.length() > 0) pl.append(", ");
        pl.append(String.format(Locale.US, "%.9f[GHz]", f));
      }
      double[] flist = new double[setF.size()];
      int k = 0;
      for (Double f : setF) flist[k++] = f;
      System.out.println("NFREQ " + flist.length);
      model.study().create("stdF");
      model.study("stdF").create("freq", "Frequency");
      model.study("stdF").feature("freq").set("plist", pl.toString());
      model.study("stdF").createAutoSequences("all");
      model.study("stdF").run();
      System.out.println("FREQ_SOLVED");
      report(model, flist, fT, fP);
      ModelUtil.remove("M5");
      System.out.println("STEP5_DONE");
    } catch (Throwable t) {
      System.out.println("STEP5_ABORT");
      t.printStackTrace(System.out);
    }
  }

  static String oneLine(Throwable ex) {
    Throwable c = (ex instanceof InvocationTargetException) ? ((InvocationTargetException) ex).getTargetException() : ex;
    String s = c.getClass().getSimpleName() + ": " + String.valueOf(c.getMessage());
    s = s.replace('\n', ' ').replace('\r', ' ').replace(',', ';');
    return s.length() > 220 ? s.substring(0, 220) : s;
  }

  static void copyGroup(Material dst, Material src, String group, boolean create) {
    if (create) dst.propertyGroup().create(group, group);
    String[] names = src.propertyGroup(group).properties();
    for (int i = 0; i < names.length; i++) {
      try { dst.propertyGroup(group).set(names[i], src.propertyGroup(group).getStringArray(names[i])); }
      catch (Exception ex) { System.out.println("skip " + group + "." + names[i]); }
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
  static int nSel(Model model, String tag) {
    try { return model.component("comp1").selection(tag).entities().length; } catch (Throwable t) { return -1; }
  }
  static String getStr(Object o, String n) {
    try { return (String) o.getClass().getMethod("getString", String.class).invoke(o, n); } catch (Throwable t) { return "ERR"; }
  }
  static void setStr(Object o, String n, String v) throws Exception { o.getClass().getMethod("set", String.class, String.class).invoke(o, n, v); }
  static void setArr(Object o, String n, String[] v) throws Exception { o.getClass().getMethod("set", String.class, String[].class).invoke(o, n, v); }

  static void build(Model model) throws Exception {
    model.param().set("p", String.format(Locale.US, "%.10f[um]", P_UM));
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
    box(model, "selLN", 2, "1[nm]", "p-1[nm]", "1[nm]", "hLn-1[nm]", "intersects");
    box(model, "selAl", 2, "1[nm]", "p-1[nm]", "hLn+1[nm]", "hLn+hAl-1[nm]", "intersects");
    box(model, "selTerm", 1, "(p-2*duty*p)/4-1[nm]", "(p-2*duty*p)/4+duty*p+1[nm]", "hLn-1[nm]", "hLn+1[nm]", "inside");
    box(model, "selGn", 1, "p/2+(p-2*duty*p)/4-1[nm]", "p/2+(p-2*duty*p)/4+duty*p+1[nm]", "hLn-1[nm]", "hLn+1[nm]", "inside");
    box(model, "selTop", 1, "-1[nm]", "p+1[nm]", "hLn-1[nm]", "hLn+1[nm]", "inside");
    box(model, "selBot", 1, "-1[nm]", "p+1[nm]", "-1[nm]", "1[nm]", "inside");
    System.out.println("GROUND_CHECK nTerm=" + nSel(model, "selTerm") + " nGround=" + nSel(model, "selGn")
        + " nTop=" + nSel(model, "selTop") + " nBot=" + nSel(model, "selBot"));
    if (nSel(model, "selTerm") != 1 || nSel(model, "selGn") != 1) throw new RuntimeException("ground check failed");

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

    model.component("comp1").variable().create("vOpt");
    model.component("comp1").variable("vOpt").selection().named("selLN");
    model.component("comp1").variable("vOpt").set("Eopt", "cos(" + String.format(Locale.US, "%.9e", KAPPA) + "[1/m]*(y-hLn/2))");
    model.component("comp1").variable("vOpt").set("Eopt2", "Eopt^2");
    model.component("comp1").variable("vOpt").set("dnPE", "-(" + String.format(Locale.US, "%.6f", NE) + "^3/2)*("
        + String.format(Locale.US, "%.6f", P31) + "*(solid.eYY+solid.eXX)+" + String.format(Locale.US, "%.6f", P33) + "*solid.eZZ)");
    model.component("comp1").variable("vOpt").set("dnEO", "-(" + String.format(Locale.US, "%.6f", NE) + "^3/2)*("
        + String.format(Locale.US, "%.3e", R13) + "[m/V]*(es.Ey-es.Ex)+" + String.format(Locale.US, "%.3e", R33) + "[m/V]*es.Ez)");

    model.physics().create("solid", "SolidMechanics", "geom1");
    model.physics().create("es", "Electrostatics", "geom1");
    model.physics("es").selection().named("selLN");
    model.physics("solid").create("pzm1", "PiezoelectricMaterialModel", 2);
    model.physics("solid").feature("pzm1").selection().named("selLN");
    model.multiphysics().create("pze1", "PiezoelectricEffect", "geom1");
    model.physics("es").create("ccp1", "ChargeConservationPiezo", 2);
    model.physics("es").feature("ccp1").selection().named("selLN");
    Object sys = model.component("comp1").coordSystem().create("sys2", "Rotated");
    setStr(sys, "rotationSequence", "ZXZ");
    setArr(sys, "angle", new String[]{"90[deg]", "0", "0"});
    setStr(model.physics("solid").feature("pzm1"), "coordinateSystem", "sys2");
    setStr(model.physics("es").feature("ccp1"), "coordinateSystem", "sys2");
    System.out.println("COORD_SYS_SET pzm1=" + getStr(model.physics("solid").feature("pzm1"), "coordinateSystem")
        + " ccp1=" + getStr(model.physics("es").feature("ccp1"), "coordinateSystem"));
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
    Object prop = model.physics("solid").prop("Type2D");
    setStr(prop, "ModeExtension", "1");
    setStr(prop, "kz", "0");
    System.out.println("TYPE2D_READBACK Type2D=" + getStr(prop, "Type2D") + " ModeExtension=" + getStr(prop, "ModeExtension") + " kz=" + getStr(prop, "kz"));
    System.out.println("ORDER_READBACK");
    model.component("comp1").cpl().create("intLN", "Integration");
    model.component("comp1").cpl("intLN").selection().geom("geom1", 2);
    model.component("comp1").cpl("intLN").selection().named("selLN");
    model.component("comp1").cpl().create("intAl", "Integration");
    model.component("comp1").cpl("intAl").selection().geom("geom1", 2);
    model.component("comp1").cpl("intAl").selection().named("selAl");
    model.component("comp1").cpl().create("intTop", "Integration");
    model.component("comp1").cpl("intTop").selection().geom("geom1", 1);
    model.component("comp1").cpl("intTop").selection().named("selTop");
    model.component("comp1").cpl().create("intBot", "Integration");
    model.component("comp1").cpl("intBot").selection().geom("geom1", 1);
    model.component("comp1").cpl("intBot").selection().named("selBot");
    model.component("comp1").cpl().create("intTerm", "Integration");
    model.component("comp1").cpl("intTerm").selection().geom("geom1", 1);
    model.component("comp1").cpl("intTerm").selection().named("selTerm");
    model.component("comp1").cpl().create("mx", "Maximum");
    model.component("comp1").cpl("mx").selection().geom("geom1", 2);
    model.component("comp1").cpl("mx").selection().named("selLN");
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
    System.out.println("NUMELEM n_elem=" + model.mesh("mesh1").getNumElem());
    model.study().create("stdE");
    model.study("stdE").create("eig", "Eigenfrequency");
    model.study("stdE").feature("eig").set("neigs", "24");
    model.study("stdE").feature("eig").set("shift", "3.33[GHz]");
    model.study("stdE").feature("eig").set("shiftactive", "on");
    model.study("stdE").createAutoSequences("all");
    System.out.println("BUILD_OK");
  }

  static int[] sideEdges(Model model, boolean lnOnly) {
    int nE = model.geom("geom1").getNEdges();
    int[] left = new int[nE], right = new int[nE];
    int nl = 0, nr = 0;
    double pmax = 0;
    for (int e = 1; e <= nE; e++) { double[][] a = model.geom("geom1").edgeX(e, new double[]{0.5}); pmax = Math.max(pmax, a[0][0]); }
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
      model.result().numerical().create("gt5", "EvalGlobal");
      model.result().numerical("gt5").set("expr", new String[]{"intLN(" + expr + ")/intLN(1)"});
      double[][] re = model.result().numerical("gt5").getReal();
      out[0] = re[0][0];
      System.out.println(String.format(Locale.US, "TENSOR expr=%s value=%.8e", expr, out[0]));
      removeNum(model, "gt5");
      return true;
    } catch (Throwable t) {
      System.out.println("TENSOR expr=" + expr + " value=UNDEFINED");
      removeNum(model, "gt5");
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
      System.out.println(String.format(Locale.US, "TENSOR_CHECK %s value=%.8e expect=%.8e ok=%s", names[i], out[0], expect[i], good));
      if (!good) ok = false;
    }
    if (!ok) throw new RuntimeException("tensor check failed");
  }

  static double[] runEigen(Model model) throws Exception {
    model.study("stdE").run();
    checkTensor(model);
    model.result().numerical().create("gevE", "EvalGlobal");
    model.result().numerical("gevE").set("expr", new String[]{
      "freq", "intLN(solid.Ws)", "intAl(solid.Ws)", "intLN(u^2)", "intLN(v^2)", "intLN(w^2)"});
    model.result().numerical("gevE").set("looplevelinput", new String[]{"all"});
    double[][] re = model.result().numerical("gevE").getReal();
    double[][] im = model.result().numerical("gevE").getImag();
    int n = re[0].length;
    double[][] rows = new double[n][8];
    for (int m = 0; m < n; m++) {
      double f = re[0][m], fi = im[0][m];
      double eL = Math.abs(re[1][m]), eA = Math.abs(re[2][m]);
      double u2 = Math.abs(re[3][m]), v2 = Math.abs(re[4][m]), w2 = Math.abs(re[5][m]);
      double et = eL + eA, ut = u2 + v2 + w2;
      rows[m][0] = f / 1e9; rows[m][1] = fi / 1e6;
      rows[m][2] = et > 0 ? eL / et : -1; rows[m][3] = et > 0 ? eA / et : -1;
      rows[m][4] = ut > 0 ? u2 / ut : -1; rows[m][5] = ut > 0 ? v2 / ut : -1; rows[m][6] = ut > 0 ? w2 / ut : -1;
      rows[m][7] = fi != 0 ? Math.abs(f / (2 * fi)) : -1;
    }
    double[] tgt = null, par = null;
    double bd = 1e9;
    for (int m = 0; m < n; m++) {
      if (rows[m][5] >= 0.80 && rows[m][2] >= 0.93 && rows[m][0] >= 3.0 && rows[m][0] <= 3.7) {
        double d = Math.abs(rows[m][0] - 3.33);
        if (d < bd) { bd = d; tgt = rows[m]; }
      }
    }
    if (tgt == null) throw new RuntimeException("no target eigenmode");
    double pd = 30.0;
    for (int m = 0; m < n; m++) {
      if (rows[m] == tgt || rows[m][5] < 0.80) continue;
      double d = Math.abs(rows[m][0] - tgt[0]) * 1000.0;
      if (d > 0 && d < pd) { pd = d; par = rows[m]; }
    }
    for (int m = 0; m < n; m++) {
      System.out.println(String.format(Locale.US, "EIG f_GHz=%.9f fi_MHz=%.6f Q=%.3f fracLN=%.4f fracAl=%.4f pu=%.3f pv=%.3f pw=%.3f",
          rows[m][0], rows[m][1], rows[m][7], rows[m][2], rows[m][3], rows[m][4], rows[m][5], rows[m][6]));
    }
    System.out.println(String.format(Locale.US, "EIG_TARGET f_GHz=%.9f fi_MHz=%.6f Q=%.3f fracLN=%.4f fracAl=%.4f pu=%.3f pv=%.3f pw=%.3f",
        tgt[0], tgt[1], tgt[7], tgt[2], tgt[3], tgt[4], tgt[5], tgt[6]));
    if (par != null) System.out.println(String.format(Locale.US, "EIG_PARTNER f_GHz=%.9f fi_MHz=%.6f Q=%.3f fracLN=%.4f fracAl=%.4f pu=%.3f pv=%.3f pw=%.3f",
        par[0], par[1], par[7], par[2], par[3], par[4], par[5], par[6]));
    System.out.println(String.format(Locale.US, "EIG_CHECK target_ok=%s partner_ok=%s",
        (Math.abs(tgt[0] - 3.329955) <= 0.0001), (par != null && Math.abs(par[0] - 3.346550) <= 0.0001)));
    removeNum(model, "gevE");
    return new double[]{tgt[0], par == null ? tgt[0] + 0.02 : par[0]};
  }

  static void removeNum(Model model, String tag) { try { model.result().numerical().remove(tag); } catch (Throwable t) {} }

  static void report(Model model, double[] flist, double fT, double fP) {
    String[] dts = model.result().dataset().tags();
    String lastDs = dts[dts.length - 1];
    System.out.println("DATASET " + lastDs + " n=" + dts.length);
    String[][] yCand = new String[][]{
      {"es.Q0_1", "i*2*pi*freq*(es.Q0_1)"},
      {"es.C11", "i*2*pi*freq*(es.C11)"},
      {"intTerm(es.Dy)", "i*2*pi*freq*intTerm(es.Dy)"},
      {"intTerm(es.nD)", "i*2*pi*freq*intTerm(es.nD)"},
      {"intTerm(es.Dx)", "i*2*pi*freq*intTerm(es.Dx)"},
      {"es.I0_1", "es.I0_1"}
    };
    String yExpr = null;
    String yLabel = null;
    for (int i = 0; i < yCand.length; i++) {
      try {
        model.result().numerical().create("chkY", "EvalGlobal");
        model.result().numerical("chkY").set("data", lastDs);
        model.result().numerical("chkY").set("expr", new String[]{yCand[i][1]});
        model.result().numerical("chkY").set("looplevelinput", new String[]{"all"});
        double[][] r = model.result().numerical("chkY").getReal();
        yExpr = yCand[i][1];
        yLabel = yCand[i][0] + " -> " + yCand[i][1];
        System.out.println("Y_EXPR_OK " + yLabel + " n=" + r[0].length + " first_Re=" + r[0][0]);
        removeNum(model, "chkY");
        break;
      } catch (Throwable t) {
        removeNum(model, "chkY");
        System.out.println("Y_EXPR_FAIL " + yCand[i][0]);
      }
    }
    if (yExpr == null) { yExpr = "i*2*pi*freq*intTerm(es.Dy)"; yLabel = "fallback intTerm(es.Dy)"; }
    System.out.println("Y_EXPR_USED " + yLabel);
    double p = P_UM * 1e-6;
    double hLn = 500e-9;
    double eTop = Math.cos(KAPPA * hLn / 2.0);
    double eTop2 = eTop * eTop;
    double nInt = computeN(eTop, hLn);
    double ne = NE, neff = NEFF;
    double cMB = (ne * ne - 1.0) * eTop2 / (2.0 * neff * nInt);
    double cPE = ne / (neff * nInt);
    List<String> exprs = new ArrayList<String>();
    exprs.add("freq");
    exprs.add(yExpr);
    exprs.add("intLN(abs(u)^2+abs(v)^2+abs(w)^2)");
    exprs.add("mx(abs(v))");
    int baseCnt = exprs.size();
    for (int n = 0; n <= NH; n++) {
      String wid = (n == 0)
          ? "(" + fmt(1.0 / p) + ")*intLN(dnPE*Eopt2)"
          : "(" + fmt(2.0 / p) + ")*intLN(dnPE*Eopt2*exp(-i*2*pi*" + n + "*x/p))";
      exprs.add(wid);
    }
    for (int n = 0; n <= NH; n++) {
      String wid = (n == 0)
          ? "(" + fmt(1.0 / p) + ")*intLN(dnEO*Eopt2)"
          : "(" + fmt(2.0 / p) + ")*intLN(dnEO*Eopt2*exp(-i*2*pi*" + n + "*x/p))";
      exprs.add(wid);
    }
    for (int n = 0; n <= NH; n++) {
      String wid = (n == 0)
          ? "(" + fmt(1.0 / p) + ")*(intTop(v)-intBot(v))"
          : "(" + fmt(2.0 / p) + ")*(intTop(v*exp(-i*2*pi*" + n + "*x/p))-intBot(v*exp(-i*2*pi*" + n + "*x/p)))";
      exprs.add(wid);
    }
    System.out.println("EXPR_COUNT " + exprs.size());
    model.result().numerical().create("gevF", "EvalGlobal");
    model.result().numerical("gevF").set("data", lastDs);
    model.result().numerical("gevF").set("expr", exprs.toArray(new String[0]));
    model.result().numerical("gevF").set("looplevelinput", new String[]{"all"});
    double[][] re = model.result().numerical("gevF").getReal();
    double[][] im = model.result().numerical("gevF").getImag();
    int nf = re[0].length;
    System.out.println("NFREQ_EVAL " + nf);
    // point check (best effort)
    pointCheck(model);
    double[] xw = new double[NWIN];
    for (int i = 0; i < NWIN; i++) xw[i] = 0.05e-6 * i;
    for (int fi = 0; fi < nf; fi++) {
      double fG = re[0][fi] / 1e9;
      double reY = re[1][fi], imY = im[1][fi];
      double iu2 = re[2][fi];
      double mv = re[3][fi];
      double[][][] qc = new double[3][NH + 1][2];
      for (int met = 0; met < 3; met++) {
        for (int n = 0; n <= NH; n++) {
          int idx = baseCnt + met * (NH + 1) + n;
          double sc = (met == 2) ? cMB : cPE;
          qc[met][n][0] = re[idx][fi] * sc;
          qc[met][n][1] = im[idx][fi] * sc;
        }
      }
      StringBuilder sb = new StringBuilder();
      sb.append(String.format(Locale.US, "SW f_GHz=%.9f ReY=%.8e ImY=%.8e int_u2=%.8e max_v=%.8e", fG, reY, imY, iu2, mv));
      int winIdx = 0;
      for (int met = 0; met < 4; met++) {
        double[] avg = (met == 3) ? totD(qc, 0) : qc[met][0];
        double[] kc = (met == 3) ? totD(qc, 1) : qc[met][1];
        double[][] ser = (met == 3) ? totSeriesD(qc) : qc[met];
        double[][] winv = new double[NWIN][];
        for (int w = 0; w < NWIN; w++) winv[w] = winSeriesD(ser, xw[w], 0.5e-6, p);
        int best = 0;
        for (int w = 1; w < NWIN; w++) if (absD(winv[w]) > absD(winv[best])) best = w;
        if (met == 3) winIdx = best;
        sb.append(String.format(Locale.US, " avgRe=%.6e avgIm=%.6e avgAbs=%.6e KRe=%.6e KIm=%.6e KAbs=%.6e winRe=%.6e winIm=%.6e winAbs=%.6e",
            avg[0], avg[1], absD(avg), kc[0], kc[1], absD(kc), winv[best][0], winv[best][1], absD(winv[best])));
      }
      sb.append(String.format(Locale.US, " win_x0_um=%.6f", xw[winIdx] * 1e6));
      System.out.println(sb.toString());
    }
    removeNum(model, "gevF");
    System.out.println("REPORT_DONE");
  }

  static String fmt(double v) { return String.format(Locale.US, "%.12e", v); }

  static double[] totD(double[][][] q, int n) {
    return new double[]{q[0][n][0] + q[1][n][0] + q[2][n][0], q[0][n][1] + q[1][n][1] + q[2][n][1]};
  }
  static double[][] totSeriesD(double[][][] q) {
    double[][] r = new double[NH + 1][2];
    for (int n = 0; n <= NH; n++) r[n] = totD(q, n);
    return r;
  }
  static double absD(double[] c) { return Math.hypot(c[0], c[1]); }
  static double[] winSeriesD(double[][] q, double x0, double w, double p) {
    double re = q[0][0], im = q[0][1];
    for (int n = 1; n <= NH; n++) {
      double th1 = 2 * Math.PI * n * x0 / p, th2 = 2 * Math.PI * n * (x0 + w) / p;
      double Ic = (Math.sin(th2) - Math.sin(th1)) / (2 * Math.PI * n * w / p);
      double Is = (-Math.cos(th2) + Math.cos(th1)) / (2 * Math.PI * n * w / p);
      double An = q[n][0], Bn = -q[n][1];
      re += An * Ic + Bn * Is;
    }
    return new double[]{re, im};
  }

  static double computeN(double eTop, double h) {
    double k = KAPPA;
    double half = h / 2;
    // core: int_0^h cos^2(k(y-h/2)) dy = h/2 + sin(k*h)/(2k)
    double core = h / 2 + Math.sin(k * h) / (2 * k);
    double e2 = eTop * eTop;
    double gam = Math.sqrt(Math.pow(1.88978, 2) - 1.0) * 2 * Math.PI / 1550e-9;
    double decay = e2 / (2 * gam) * 2.0; // both claddings above and below
    return core + decay;
  }

  static void pointCheck(Model model) {
    try {
      model.result().dataset().create("cpt1", "CutPoint2D");
      model.result().dataset("cpt1").set("pointx", "p/2");
      model.result().dataset("cpt1").set("pointy", "hLn/2");
      model.result().numerical().create("pev1", "EvalPoint");
      model.result().numerical("pev1").set("data", "cpt1");
      model.result().numerical("pev1").set("expr", new String[]{"es.Ex", "es.Ey", "solid.eXX", "solid.eYY"});
      model.result().numerical("pev1").set("looplevelinput", new String[]{"first"});
      double[][] r = model.result().numerical("pev1").getReal();
      System.out.println(String.format(Locale.US, "POINT_CHECK es.Ex=%.6e es.Ey=%.6e solid.eXX=%.6e solid.eYY=%.6e",
          r[0][0], r[1][0], r[2][0], r[3][0]));
      removeNum(model, "pev1");
    } catch (Throwable t) {
      System.out.println("POINT_CHECK_NA " + oneLine(t));
    }
  }

  static class Complex {
    double re, im;
    Complex(double re, double im) { this.re = re; this.im = im; }
    Complex scale(double s) { return new Complex(re * s, im * s); }
    double abs() { return Math.hypot(re, im); }
  }
}
