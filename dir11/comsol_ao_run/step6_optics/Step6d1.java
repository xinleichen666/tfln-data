import com.comsol.model.*;
import com.comsol.model.util.*;
import java.lang.reflect.*;
import java.util.*;

/** Step 6d-1: 400 nm slab unit cell. Coarse period sweep, target by fracAl, secant to 3.330 GHz, 1 V drive check at P_NEW. */
public class Step6d1 {
  static final String PZ = "D:\\COMSOL63\\Multiphysics\\data\\comsol_piezo_lib.mph";
  static final String BASIC = "D:\\COMSOL63\\Multiphysics\\data\\comsol_basic_material_lib.mph";
  static final double FGOAL = 3.330;

  public static void main(String[] args) {
    try {
      ModelUtil.initStandalone(true);
      System.out.println("STEP6D1_START");
      Model model = ModelUtil.create("M6d1");
      build(model);
      TreeMap<Double,double[]> track = new TreeMap<>();
      for (int i = 0; i <= 8; i++) {
        double p = 2.0 + 0.2 * i;
        setPeriod(model, p, true);
        List<double[]> modes = solveModes(model, p, "coarse", false);
        printCands(modes, p, "COARSE");
        double[] t = pickTarget(modes, FGOAL);
        if (t == null) { System.out.println(String.format(Locale.US, "COARSE_TARGET p_um=%.6f NONE", p)); continue; }
        double[] pa = nearestCand(modes, t, 0.050);
        track.put(p, t);
        System.out.println(String.format(Locale.US, "COARSE_TARGET p_um=%.6f f_GHz=%.6f fracAl=%.4f pv=%.3f pw=%.3f partner_f_GHz=%s partner_fracAl=%s",
            p, t[0], t[3], t[5], t[6], pa == null ? "NA" : String.format(Locale.US, "%.6f", pa[0]), pa == null ? "NA" : String.format(Locale.US, "%.4f", pa[3])));
      }
      double p1 = Double.NaN, p2 = Double.NaN, f1 = 0, f2 = 0;
      Double[] keys = track.keySet().toArray(new Double[0]);
      for (int i = 0; i + 1 < keys.length; i++) {
        double pa = keys[i], pb = keys[i + 1];
        double fa = track.get(pa)[0], fb = track.get(pb)[0];
        if ((fa - FGOAL) * (fb - FGOAL) <= 0 && fa != fb) { p1 = pa; p2 = pb; f1 = fa; f2 = fb; break; }
      }
      if (Double.isNaN(p1)) throw new RuntimeException("no bracket crossing 3.330");
      System.out.println(String.format(Locale.US, "SECANT_START p1=%.6f f1=%.6f p2=%.6f f2=%.6f", p1, f1, p2, f2));
      double pNew = Double.NaN; double[] tN = null, paN = null;
      for (int it = 1; it <= 12; it++) {
        double p = p1 + (FGOAL - f1) * (p2 - p1) / (f2 - f1);
        setPeriod(model, p, false);
        List<double[]> modes = solveModes(model, p, "secant", false);
        double[] t = pickTarget(modes, FGOAL);
        if (t == null) throw new RuntimeException("secant target not found");
        double[] pa = nearestCand(modes, t, 0.050);
        System.out.println(String.format(Locale.US, "SECANT_ITER it=%d p_um=%.8f f_GHz=%.6f fracAl=%.4f pv=%.3f pw=%.3f partner_f_GHz=%s partner_fracAl=%s",
            it, p, t[0], t[3], t[5], t[6], pa == null ? "NA" : String.format(Locale.US, "%.6f", pa[0]), pa == null ? "NA" : String.format(Locale.US, "%.4f", pa[3])));
        if (Math.abs(t[0] - FGOAL) < 0.001) { pNew = p; tN = t; paN = pa; printCands(modes, p, "PNEW"); break; }
        if ((t[0] - FGOAL) * (f1 - FGOAL) > 0) { p1 = p; f1 = t[0]; } else { p2 = p; f2 = t[0]; }
      }
      if (tN == null) throw new RuntimeException("secant did not converge");
      double qT = tN[1] != 0 ? Math.abs(tN[0] * 1e3 / (2 * tN[1])) : -1;
      System.out.println(String.format(Locale.US, "P_NEW p_um=%.8f f_GHz=%.6f Q_eig=%.1f fracLN=%.4f fracAl=%.4f pv=%.3f pw=%.3f partner_f_GHz=%s partner_fracAl=%s",
          pNew, tN[0], qT, tN[2], tN[3], tN[5], tN[6], paN == null ? "NA" : String.format(Locale.US, "%.6f", paN[0]), paN == null ? "NA" : String.format(Locale.US, "%.4f", paN[3])));
      drive(model, tN[0], paN == null ? Double.NaN : paN[0]);
      ModelUtil.remove("M6d1");
      System.out.println("STEP6D1_DONE");
    } catch (Throwable t) {
      System.out.println("STEP6D1_ABORT");
      t.printStackTrace(System.out);
    }
  }

  static boolean isCand(double[] r) { return r[5] >= 0.80 && r[2] >= 0.93 && r[0] >= 2.8 && r[0] <= 3.9; }

  static double[] nearestCand(List<double[]> modes, double[] t, double maxGHz) {
    double[] best = null; double bd = maxGHz;
    for (double[] r : modes) {
      if (r == t || r[5] < 0.80) continue;
      double d = Math.abs(r[0] - t[0]);
      if (d > 0 && d < bd) { bd = d; best = r; }
    }
    return best;
  }

  /** Driven mode = the one of a pv>=0.8 pair with the smaller fracAl; candidates without a pair within 50 MHz are not used. */
  static double[] pickTarget(List<double[]> modes, double fRef) {
    double[] best = null; double bd = 1e9;
    for (double[] r : modes) {
      if (!isCand(r)) continue;
      double[] pa = nearestCand(modes, r, 0.050);
      if (pa == null || pa[3] <= r[3]) continue;
      double d = Math.abs(r[0] - fRef);
      if (d < bd) { bd = d; best = r; }
    }
    return best;
  }

  static void printCands(List<double[]> modes, double p, String tag) {
    for (double[] r : modes) {
      if (!isCand(r)) continue;
      double[] pa = nearestCand(modes, r, 0.050);
      String role = pa == null ? "single" : (pa[3] > r[3] ? "driven" : "partner");
      StringBuilder near = new StringBuilder();
      for (double[] q : modes) {
        if (q == r || Math.abs(q[0] - r[0]) > 0.003) continue;
        near.append(String.format(Locale.US, " [f=%.6f fracAl=%.4f pv=%.3f pw=%.3f]", q[0], q[3], q[5], q[6]));
      }
      System.out.println(String.format(Locale.US, "%s_CAND p_um=%.6f f_GHz=%.6f fracLN=%.4f fracAl=%.4f pv=%.3f pw=%.3f role=%s nearest_pv08_f_GHz=%s nearest_fracAl=%s within3MHz=%s",
          tag, p, r[0], r[2], r[3], r[5], r[6], role,
          pa == null ? "NA" : String.format(Locale.US, "%.6f", pa[0]), pa == null ? "NA" : String.format(Locale.US, "%.4f", pa[3]),
          near.length() == 0 ? "none" : near.toString().trim()));
    }
  }

  static void drive(Model model, double fT, double fP) throws Exception {
    model.physics("es").feature().remove("gndT");
    model.physics("es").create("term1", "Terminal", 1);
    model.physics("es").feature("term1").selection().named("selTerm");
    model.physics("es").feature("term1").set("TerminalType", "Voltage");
    model.physics("es").feature("term1").set("V0", "1[V]");
    TreeSet<Double> setF = new TreeSet<Double>();
    for (int i = 0; i <= 60; i++) setF.add(Math.round((3.30 + 0.001 * i) * 1e9) / 1e9);
    for (int i = -40; i <= 40; i++) setF.add(Math.round((fT + 0.00005 * i) * 1e9) / 1e9);
    if (!Double.isNaN(fP) && fP > 3.29 && fP < 3.37) for (int i = -40; i <= 40; i++) setF.add(Math.round((fP + 0.00005 * i) * 1e9) / 1e9);
    StringBuilder pl = new StringBuilder();
    for (Double f : setF) { if (pl.length() > 0) pl.append(", "); pl.append(String.format(Locale.US, "%.9f[GHz]", f)); }
    System.out.println("DRIVE_NFREQ " + setF.size() + " (3.30-3.36 GHz step 1 MHz + 50 kHz around eigen f_target/f_partner)");
    model.study().create("stdF");
    model.study("stdF").create("freq", "Frequency");
    model.study("stdF").feature("freq").set("plist", pl.toString());
    model.study("stdF").createAutoSequences("all");
    model.study("stdF").run();
    String[] dts = model.result().dataset().tags();
    String ds = dts[dts.length - 1];
    model.result().numerical().create("gY", "EvalGlobal");
    model.result().numerical("gY").set("data", ds);
    model.result().numerical("gY").set("expr", new String[]{"freq", "i*2*pi*freq*(es.Q0_1)"});
    model.result().numerical("gY").set("looplevelinput", new String[]{"all"});
    double[][] re = model.result().numerical("gY").getReal();
    double[][] im = model.result().numerical("gY").getImag();
    int n = re[0].length;
    int iG = 0, iA = 0;
    for (int k = 0; k < n; k++) {
      double f = re[0][k] / 1e9, g = re[1][k], b = im[1][k];
      System.out.println(String.format(Locale.US, "DRIVE f_GHz=%.6f ReY=%.6e ImY=%.6e absY=%.6e", f, g, b, Math.hypot(g, b)));
      if (g > re[1][iG]) iG = k;
      if (Math.hypot(g, b) > Math.hypot(re[1][iA], im[1][iA])) iA = k;
    }
    double fG = re[0][iG] / 1e9, gMax = re[1][iG];
    double lo = Double.NaN, hi = Double.NaN;
    for (int k = iG; k > 0; k--) if (re[1][k - 1] < gMax / 2) { lo = interp(re[0][k - 1], re[1][k - 1], re[0][k], re[1][k], gMax / 2) / 1e9; break; }
    for (int k = iG; k < n - 1; k++) if (re[1][k + 1] < gMax / 2) { hi = interp(re[0][k], re[1][k], re[0][k + 1], re[1][k + 1], gMax / 2) / 1e9; break; }
    double q = (!Double.isNaN(lo) && !Double.isNaN(hi)) ? fG / (hi - lo) : -1;
    boolean nearT = Double.isNaN(fP) || Math.abs(fG - fT) < Math.abs(fG - fP);
    System.out.println(String.format(Locale.US, "DRIVE_PEAK f_peak_ReY_GHz=%.6f ReY_max=%.6e FWHM_MHz=%.4f Q=%.1f f_peak_absY_GHz=%.6f f_target_eig=%.6f f_partner_eig=%s df_peak_target_MHz=%.3f peak_on_target=%b",
        fG, gMax, (hi - lo) * 1e3, q, re[0][iA] / 1e9, fT, Double.isNaN(fP) ? "NA" : String.format(Locale.US, "%.6f", fP), (fG - fT) * 1e3, nearT));
    model.result().numerical().remove("gY");
  }
  static double interp(double x0, double y0, double x1, double y1, double y) { return x0 + (y - y0) * (x1 - x0) / (y1 - y0); }

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
    try { return model.component("comp1").selection(tag).entities().length; }
    catch (Throwable t) { return -1; }
  }
  static String getStr(Object o, String n) {
    try { return (String) o.getClass().getMethod("getString", String.class).invoke(o, n); }
    catch (Throwable t) { return "ERR"; }
  }
  static void setStr(Object o, String n, String v) throws Exception {
    o.getClass().getMethod("set", String.class, String.class).invoke(o, n, v);
  }
  static void setArr(Object o, String n, String[] v) throws Exception {
    o.getClass().getMethod("set", String.class, String[].class).invoke(o, n, v);
  }
  static String oneLine(Throwable ex) {
    String s = ex.getClass().getSimpleName() + ": " + String.valueOf(ex.getMessage());
    s = s.replace('\n', ' ').replace('\r', ' ').replace(',', ';');
    return s.length() > 220 ? s.substring(0, 220) : s;
  }

  static void build(Model model) throws Exception {
    model.param().set("p", "2.8326[um]");
    model.param().set("hLn", "400[nm]");
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
    ModelUtil.remove("pz"); ModelUtil.remove("basic");
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
    Object prop = model.physics("solid").prop("Type2D");
    setStr(prop, "ModeExtension", "1");
    setStr(prop, "kz", "0");
    System.out.println("TYPE2D_READBACK Type2D=" + getStr(prop, "Type2D") + " ModeExtension=" + getStr(prop, "ModeExtension") + " kz=" + getStr(prop, "kz"));
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
    model.study().create("stdE");
    model.study("stdE").create("eig", "Eigenfrequency");
    model.study("stdE").feature("eig").set("neigs", "24");
    model.study("stdE").feature("eig").set("shift", "3.0[GHz]");
    model.study("stdE").feature("eig").set("shiftactive", "on");
    model.study("stdE").createAutoSequences("all");
    System.out.println("BUILD_OK hLn=400[nm]");
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
      if (lnOnly && (ylo < -1e-9 || yhi > 400e-9 + 1e-9)) continue;
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

  static void setPeriod(Model model, double pUm, boolean verbose) throws Exception {
    model.param().set("p", String.format(Locale.US, "%.8f[um]", pUm));
    model.geom("geom1").run();
    applyPeriodic(model);
    model.component("comp1").cpl("intLN").selection().named("selLN");
    model.component("comp1").cpl("intAl").selection().named("selAl");
    model.physics("solid").feature("pzm1").selection().named("selLN");
    model.physics("es").feature("ccp1").selection().named("selLN");
    model.physics("es").feature("gndT").selection().named("selTerm");
    model.physics("es").feature("gnd1").selection().named("selGn");
    model.mesh("mesh1").run();
    int nt = nSel(model, "selTerm");
    int ng = nSel(model, "selGn");
    if (verbose) System.out.println(String.format(Locale.US, "PERIOD p_um=%.6f nGroundT=%d nGroundG=%d", pUm, nt, ng));
    if (nt != 1 || ng != 1) throw new RuntimeException("ground check failed at p=" + pUm + ": " + nt + "/" + ng);
  }

  static List<double[]> solveModes(Model model, double pUm, String variant, boolean printAll) {
    try {
      model.study("stdE").run();
      model.result().numerical().create("gevP", "EvalGlobal");
      model.result().numerical("gevP").set("expr", new String[]{
        "freq", "intLN(solid.Ws)", "intAl(solid.Ws)", "intLN(u^2)", "intLN(v^2)", "intLN(w^2)"
      });
      model.result().numerical("gevP").set("looplevelinput", new String[]{"all"});
      double[][] re = model.result().numerical("gevP").getReal();
      double[][] im = model.result().numerical("gevP").getImag();
      List<double[]> list = new ArrayList<double[]>();
      int n = re[0].length;
      for (int m = 0; m < n; m++) {
        double f = re[0][m], fi = im[0][m];
        double eL = Math.abs(re[1][m]), eA = Math.abs(re[2][m]);
        double u2 = Math.abs(re[3][m]), v2 = Math.abs(re[4][m]), w2 = Math.abs(re[5][m]);
        double et = eL + eA, ut = u2 + v2 + w2;
        double fl = et > 0 ? eL / et : -1, fa = et > 0 ? eA / et : -1;
        double pu = ut > 0 ? u2 / ut : -1, pv = ut > 0 ? v2 / ut : -1, pw = ut > 0 ? w2 / ut : -1;
        list.add(new double[]{f / 1e9, fi / 1e6, fl, fa, pu, pv, pw});
        if (printAll) {
          System.out.println(String.format(Locale.US,
              "ROW variant=%s p_um=%.6f f_GHz=%.6f fi_MHz=%.4f fracLN=%.4f fracAl=%.4f pu=%.3f pv=%.3f pw=%.3f",
              variant, pUm, f / 1e9, fi / 1e6, fl, fa, pu, pv, pw));
        }
      }
      double fmin = 1e9, fmax = -1e9;
      for (double[] r : list) { fmin = Math.min(fmin, r[0]); fmax = Math.max(fmax, r[0]); }
      System.out.println(String.format(Locale.US, "SOLVED variant=%s p_um=%.6f nmodes=%d f_range_GHz=[%.4f,%.4f]", variant, pUm, n, fmin, fmax));
      try { model.result().numerical().remove("gevP"); } catch (Throwable t) {}
      return list;
    } catch (Throwable t) {
      System.out.println("SOLVE_FAIL p_um=" + pUm + " " + oneLine(t));
      return new ArrayList<double[]>();
    }
  }
}
