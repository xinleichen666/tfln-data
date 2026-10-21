import com.comsol.model.*;
import com.comsol.model.util.*;
import java.lang.reflect.*;
import java.util.*;
import java.io.*;

/** Step 4 Part C: 2D-B period sweep, target tracking, secant to 3.330 GHz, write pnew.txt. */
public class Step4PartC2D {
  static final String PZ = "D:\\COMSOL63\\Multiphysics\\data\\comsol_piezo_lib.mph";
  static final String BASIC = "D:\\COMSOL63\\Multiphysics\\data\\comsol_basic_material_lib.mph";
  static final String PNEW = "D:\\comsol_ao_run\\step4_fixed\\pnew.txt";
  static final double FGOAL = 3.330;

  public static void main(String[] args) {
    try {
      ModelUtil.initStandalone(true);
      System.out.println("STEP4_C2D_START");
      Model model = ModelUtil.create("M4C");
      build(model);
      // initial point
      setPeriod(model, 2.8326, true);
      List<double[]> modes0 = solveModes(model, 2.8326, "2D-B-init", true);
      double[] t0 = findTarget(modes0);
      if (t0 == null) throw new RuntimeException("no initial target at p=2.8326");
      double[] p0 = partner(modes0, t0);
      System.out.println(String.format(Locale.US, "TRACK_POINT p_um=2.832600 f_target_GHz=%.6f pv=%.3f pw=%.3f fracAl=%.4f f_partner_GHz=%s",
          t0[0], t0[5], t0[6], t0[3], p0 == null ? "NA" : String.format(Locale.US, "%.6f", p0[0])));
      double refFracAl = t0[3];
      double refF = t0[0];
      // sweep outward
      double[] up = new double[]{2.85,2.90,2.95,3.00,3.05,3.10,3.15,3.20};
      double[] dn = new double[]{2.80,2.75,2.70,2.65,2.60,2.55,2.50,2.45,2.40};
      TreeMap<Double,double[]> track = new TreeMap<>();
      track.put(2.8326, t0);
      for (int i = 0; i < up.length; i++) {
        double p = up[i];
        setPeriod(model, p, true);
        List<double[]> modes = solveModes(model, p, "2D-B", true);
        double[] t = trackMode(modes, refFracAl, refF);
        if (t == null) { System.out.println(String.format(Locale.US, "TRACK_POINT p_um=%.6f f_target_GHz=NA", p)); continue; }
        double[] pa = partner(modes, t);
        refFracAl = t[3]; refF = t[0];
        track.put(p, t);
        System.out.println(String.format(Locale.US, "TRACK_POINT p_um=%.6f f_target_GHz=%.6f pv=%.3f pw=%.3f fracAl=%.4f f_partner_GHz=%s",
            p, t[0], t[5], t[6], t[3], pa == null ? "NA" : String.format(Locale.US, "%.6f", pa[0])));
      }
      refFracAl = t0[3]; refF = t0[0];
      for (int i = 0; i < dn.length; i++) {
        double p = dn[i];
        setPeriod(model, p, true);
        List<double[]> modes = solveModes(model, p, "2D-B", true);
        double[] t = trackMode(modes, refFracAl, refF);
        if (t == null) { System.out.println(String.format(Locale.US, "TRACK_POINT p_um=%.6f f_target_GHz=NA", p)); continue; }
        double[] pa = partner(modes, t);
        refFracAl = t[3]; refF = t[0];
        track.put(p, t);
        System.out.println(String.format(Locale.US, "TRACK_POINT p_um=%.6f f_target_GHz=%.6f pv=%.3f pw=%.3f fracAl=%.4f f_partner_GHz=%s",
            p, t[0], t[5], t[6], t[3], pa == null ? "NA" : String.format(Locale.US, "%.6f", pa[0])));
      }
      // find adjacent bracket crossing FGOAL among ascending p
      double p1 = Double.NaN, p2 = Double.NaN, f1 = 0, f2 = 0;
      Double[] keys = track.keySet().toArray(new Double[0]);
      for (int i = 0; i + 1 < keys.length; i++) {
        double pa = keys[i].doubleValue(), pb = keys[i + 1].doubleValue();
        double fa = track.get(pa)[0], fb = track.get(pb)[0];
        if ((fa - FGOAL) * (fb - FGOAL) <= 0 && fa != fb) { p1 = pa; p2 = pb; f1 = fa; f2 = fb; break; }
      }
      if (Double.isNaN(p1)) throw new RuntimeException("no bracket crossing 3.330");
      System.out.println(String.format(Locale.US, "SECANT_START p1=%.6f f1=%.6f p2=%.6f f2=%.6f", p1, f1, p2, f2));
      double refFA = track.get(p1)[3];
      double pN = p2;
      for (int it = 1; it <= 10; it++) {
        double p = p1 + (FGOAL - f1) * (p2 - p1) / (f2 - f1);
        setPeriod(model, p, true);
        List<double[]> modes = solveModes(model, p, "2D-B", false);
        double[] t = trackMode(modes, refFA, f1 + (f2 - f1) * (p - p1) / (p2 - p1));
        if (t == null) throw new RuntimeException("secant target not found");
        double[] pa = partner(modes, t);
        System.out.println(String.format(Locale.US,
            "SECANT_ITER it=%d p_um=%.8f f_GHz=%.6f pv=%.3f pw=%.3f fracAl=%.4f f_partner_GHz=%s",
            it, p, t[0], t[5], t[6], t[3], pa == null ? "NA" : String.format(Locale.US, "%.6f", pa[0])));
        pN = p;
        if (Math.abs(t[0] - FGOAL) < 0.001) {
          System.out.println(String.format(Locale.US, "P_NEW p_um=%.8f f_GHz=%.6f pv=%.3f pw=%.3f fracAl=%.4f f_partner_GHz=%s",
              p, t[0], t[5], t[6], t[3], pa == null ? "NA" : String.format(Locale.US, "%.6f", pa[0])));
          // final 2D-B at p_new: full 24 modes with variant tag
          List<double[]> fin = solveModes(model, p, "2D-B-pnew", true);
          PrintWriter pw = new PrintWriter(new OutputStreamWriter(new FileOutputStream(PNEW), "UTF-8"));
          pw.println(String.format(Locale.US, "%.10f,%.6f,%s,%.4f,%.3f,%.4f",
              p, t[0], pa == null ? "NA" : String.format(Locale.US, "%.6f", pa[0]), t[3], t[5], t[6]));
          pw.close();
          break;
        }
        if (t[0] < FGOAL) { p1 = p; f1 = t[0]; } else { p2 = p; f2 = t[0]; }
        refFA = t[3];
      }
      model.study("stdE");
      ModelUtil.remove("M4C");
      System.out.println("STEP4_C2D_DONE");
    } catch (Throwable t) {
      System.out.println("STEP4_C2D_ABORT");
      t.printStackTrace(System.out);
    }
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
  static Throwable unwrap(Throwable t) { return (t instanceof InvocationTargetException) ? ((InvocationTargetException) t).getTargetException() : t; }
  static String oneLine(Throwable ex) {
    String s = ex.getClass().getSimpleName() + ": " + String.valueOf(ex.getMessage());
    s = s.replace('\n', ' ').replace('\r', ' ').replace(',', ';');
    return s.length() > 220 ? s.substring(0, 220) : s;
  }

  static void build(Model model) throws Exception {
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
              "ROW variant=%s p_um=%.6f dim=2 part=C f_GHz=%.6f fi_MHz=%.4f fracLN=%.4f fracAl=%.4f pu=%.3f pv=%.3f pw=%.3f orient=sys",
              variant, pUm, f / 1e9, fi / 1e6, fl, fa, pu, pv, pw));
        }
      }
      for (int m = 0; m < list.size(); m++) {
        double[] r = list.get(m);
        if (r[0] >= 3.0 && r[0] <= 3.7 && r[5] >= 0.80) {
          System.out.println(String.format(Locale.US,
              "SWEEP_PMODE p_um=%.6f f_GHz=%.6f pv=%.3f pw=%.3f fracLN=%.4f fracAl=%.4f",
              pUm, r[0], r[5], r[6], r[2], r[3]));
        }
      }
      try { model.result().numerical().remove("gevP"); } catch (Throwable t) {}
      return list;
    } catch (Throwable t) {
      System.out.println("SOLVE_FAIL p_um=" + pUm + " " + oneLine(t));
      return new ArrayList<double[]>();
    }
  }

  static double[] findTarget(List<double[]> modes) {
    double[] best = null;
    double bd = 1e9;
    for (int i = 0; i < modes.size(); i++) {
      double[] r = modes.get(i);
      if (r[5] >= 0.80 && r[2] >= 0.93 && r[0] >= 3.0 && r[0] <= 3.7) {
        double d = Math.abs(r[0] - FGOAL);
        if (d < bd) { bd = d; best = r; }
      }
    }
    return best;
  }
  static double[] trackMode(List<double[]> modes, double refFracAl, double refF) {
    double[] best = null;
    double bs = 1e9;
    for (int i = 0; i < modes.size(); i++) {
      double[] r = modes.get(i);
      if (r[5] < 0.80) continue;
      double score = Math.abs(r[3] - refFracAl) * 1.0 + Math.abs(r[0] - refF) * 0.05;
      if (score < bs) { bs = score; best = r; }
    }
    return best;
  }
  static double[] partner(List<double[]> modes, double[] t) {
    double[] best = null;
    double bd = 30.0;
    for (int i = 0; i < modes.size(); i++) {
      double[] r = modes.get(i);
      if (r == t || r[5] < 0.80) continue;
      double d = Math.abs(r[0] - t[0]) * 1000.0;
      if (d > 0 && d < bd) { bd = d; best = r; }
    }
    return best;
  }
}
