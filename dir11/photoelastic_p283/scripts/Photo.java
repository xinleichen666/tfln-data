import com.comsol.model.*;
import com.comsol.model.util.*;

/**
 * Suspended plate, 1 V on one electrode, at the coupled vertical-mode frequency.
 * Photoelastic tensor: Weis and Gaylord, Appl. Phys. A 37, 191 (1985), about 633 nm,
 * as tabulated by Andrushchak et al., J. Appl. Phys. 106, 073510 (2009), Ref. 22.
 * Indices at 1550 nm: Zelmon et al., n_o = 2.211, n_e = 2.138.
 * Flat slab, etch = 0. Moving boundary is not included.
 */
public class Photo {
  static final String PZ = "D:\\COMSOL63\\Multiphysics\\data\\comsol_piezo_lib.mph";
  static final String BASIC = "D:\\COMSOL63\\Multiphysics\\data\\comsol_basic_material_lib.mph";
  static final double NO = 2.211;
  static final double NE = 2.138;
  static final double P11 = -0.026;
  static final double P12 = 0.090;
  static final double P13 = 0.133;
  static final double P31 = 0.179;
  static final double P33 = 0.071;
  static final double LA = 100e-6;
  static final double LRING = 0.667e-3;
  static final double FOPT = 193.4e12;
  static final double GHzV = 21.3;

  public static void main(String[] args) throws Exception {
    double lambda = 2.99792458e8 / FOPT;
    double[] te = slab(lambda, NE, 500e-9);
    double[] te2 = slab(lambda * 1.001, NE, 500e-9);
    double[] tm = slab(lambda, NO, 500e-9);
    double[] tm2 = slab(lambda * 1.001, NO, 500e-9);
    double ngTE = te[0] - lambda * (te2[0] - te[0]) / (0.001 * lambda);
    double ngTM = tm[0] - lambda * (tm2[0] - tm[0]) / (0.001 * lambda);
    System.out.println(String.format(java.util.Locale.US,
        "SLAB_TE neff=%.5f ng=%.5f GammaE=%.4f kappa=%.6e", te[0], ngTE, te[3], te[1]));
    System.out.println(String.format(java.util.Locale.US,
        "SLAB_TM neff=%.5f ng=%.5f GammaE=%.4f kappa=%.6e", tm[0], ngTM, tm[3], tm[1]));

    ModelUtil.initStandalone(true);
    Model model = ModelUtil.create("Model");
    model.modelPath("D:\\comsol_ao_run\\photoelastic");
    model.label("photoelastic.mph");
    try {
      build(model, te[1], tm[1]);
      double pNow = 2.8326;
      setPeriod(model, pNow);
      double fNow = eigenNear(model, 3.33e9);
      if (Math.abs(fNow - 3.33e9) > 8e6) {
        double p2 = pNow + (3.33e9 - fNow) / (-1.505e9);
        setPeriod(model, p2);
        fNow = eigenNear(model, 3.33e9);
        pNow = p2;
      }
      double finger = 0.25 * pNow;
      System.out.println(String.format(java.util.Locale.US,
          "LOCKED p_um=%.4f finger_um=%.4f f_GHz=%.6f k=%.6e",
          pNow, finger, fNow / 1e9, 2 * Math.PI / (pNow * 1e-6)));
      drive(model, fNow, te[0], ngTE, te[3], tm[0], ngTM, tm[3]);
    } catch (Throwable ex) {
      ex.printStackTrace(System.out);
    }
  }

  static double[] slab(double lambda, double n, double h) {
    double d = h / 2;
    double k0 = 2 * Math.PI / lambda;
    double lo = 1.2;
    double hi = n - 1e-6;
    for (int it = 0; it < 80; it++) {
      double mid = 0.5 * (lo + hi);
      double kappa = k0 * Math.sqrt(n * n - mid * mid);
      double gam = k0 * Math.sqrt(mid * mid - 1);
      double f = gam - kappa * Math.tan(kappa * d);
      if (f > 0) hi = mid;
      else lo = mid;
    }
    double neff = 0.5 * (lo + hi);
    double kappa = k0 * Math.sqrt(n * n - neff * neff);
    double gam = k0 * Math.sqrt(neff * neff - 1);
    double icore = d + Math.sin(2 * kappa * d) / (2 * kappa);
    double iclad = Math.cos(kappa * d) * Math.cos(kappa * d) / (2 * gam);
    double gE = icore / (icore + 2 * iclad);
    return new double[]{neff, kappa, gam, gE};
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

  static void box(Model model, String tag, String xmin, String xmax, String ymin, String ymax) {
    model.component("comp1").selection().create(tag, "Box");
    boolean boundary = tag.equals("selTerm") || tag.equals("selGn");
    model.component("comp1").selection(tag).set("entitydim", boundary ? "1" : "2");
    model.component("comp1").selection(tag).set("condition", "intersects");
    model.component("comp1").selection(tag).set("xmin", xmin);
    model.component("comp1").selection(tag).set("xmax", xmax);
    model.component("comp1").selection(tag).set("ymin", ymin);
    model.component("comp1").selection(tag).set("ymax", ymax);
  }

  static void build(Model model, double kappaTE, double kappaTM) throws Exception {
    model.param().set("p", "2.58[um]");
    model.param().set("hLn", "500[nm]");
    model.param().set("hAl", "100[nm]");
    model.param().set("duty", "0.25");
    model.param().set("p11", Double.toString(P11));
    model.param().set("p12", Double.toString(P12));
    model.param().set("p13", Double.toString(P13));
    model.param().set("p31", Double.toString(P31));
    model.param().set("p33", Double.toString(P33));
    model.param().set("no", Double.toString(NO));
    model.param().set("ne", Double.toString(NE));
    model.param().set("kTE", kappaTE + "[1/m]");
    model.param().set("kTM", kappaTM + "[1/m]");

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

    box(model, "selLN", "1[nm]", "p-1[nm]", "1[nm]", "hLn-1[nm]");
    box(model, "selAl", "1[nm]", "p-1[nm]", "hLn+1[nm]", "hLn+hAl-1[nm]");
    box(model, "selTerm", "(p-2*duty*p)/4-1[nm]", "(p-2*duty*p)/4+duty*p+1[nm]", "hLn-1[nm]", "hLn+1[nm]");
    box(model, "selGn", "p/2+(p-2*duty*p)/4-1[nm]", "p/2+(p-2*duty*p)/4+duty*p+1[nm]", "hLn-1[nm]", "hLn+1[nm]");

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

    model.component("comp1").variable().create("var1");
    model.component("comp1").variable("var1").selection().named("selLN");
    model.component("comp1").variable("var1").set("S1", "solid.eYY");
    model.component("comp1").variable("var1").set("S2", "solid.eXX");
    model.component("comp1").variable("var1").set("S3", "solid.eZZ");
    model.component("comp1").variable("var1").set("dB3", "p31*(S1+S2)+p33*S3");
    model.component("comp1").variable("var1").set("dB1", "p11*S1+p12*S2+p13*S3");
    model.component("comp1").variable("var1").set("dnZ", "-(ne^3/2)*dB3");
    model.component("comp1").variable("var1").set("dnX", "-(no^3/2)*dB1");
    model.component("comp1").variable("var1").set("wTE", "cos(kTE*(y-hLn/2))^2");
    model.component("comp1").variable("var1").set("wTM", "cos(kTM*(y-hLn/2))^2");

    model.physics().create("solid", "SolidMechanics", "geom1");
    model.physics().create("es", "Electrostatics", "geom1");
    model.physics("es").selection().named("selLN");
    model.physics("solid").create("pzm1", "PiezoelectricMaterialModel", 2);
    model.physics("solid").feature("pzm1").selection().named("selLN");
    model.multiphysics().create("pze1", "PiezoelectricEffect", "geom1");
    model.physics("es").create("ccp1", "ChargeConservationPiezo", 2);
    model.physics("es").feature("ccp1").selection().named("selLN");
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

    model.component("comp1").cpl().create("intLN", "Integration");
    model.component("comp1").cpl("intLN").selection().geom("geom1", 2);
    model.component("comp1").cpl("intLN").selection().named("selLN");
    model.component("comp1").cpl().create("intAl", "Integration");
    model.component("comp1").cpl("intAl").selection().geom("geom1", 2);
    model.component("comp1").cpl("intAl").selection().named("selAl");
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

    model.study().create("stdE");
    model.study("stdE").create("eig", "Eigenfrequency");
    model.study("stdE").feature("eig").set("neigs", "16");
    model.study("stdE").feature("eig").set("shift", "3.33[GHz]");
    model.study("stdE").feature("eig").set("shiftactive", "on");
    model.study("stdE").createAutoSequences("all");
    System.out.println("BUILD_OK domainsLN=" + model.physics("es").feature("ccp1").selection().entities().length);
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

  static void setPeriod(Model model, double pUm) {
    System.out.println(String.format(java.util.Locale.US, "PERIOD %.4f", pUm));
    model.param().set("p", String.format(java.util.Locale.US, "%.6f[um]", pUm));
    model.geom("geom1").run();
    applyPeriodic(model);
    model.component("comp1").cpl("intLN").selection().named("selLN");
    model.component("comp1").cpl("intAl").selection().named("selAl");
    model.component("comp1").cpl("mx").selection().named("selLN");
    model.physics("solid").feature("pzm1").selection().named("selLN");
    model.physics("es").feature("ccp1").selection().named("selLN");
    model.physics("es").feature("gndT").selection().named("selTerm");
    model.physics("es").feature("gnd1").selection().named("selGn");
    model.mesh("mesh1").run();
  }

  static double eigenNear(Model model, double hintHz) {
    model.study("stdE").run();
    try { model.result().numerical().remove("gevE"); } catch (Exception ex) {}
    model.result().numerical().create("gevE", "EvalGlobal");
    model.result().numerical("gevE").set("expr", new String[]{
      "freq", "intLN(solid.Ws)", "intAl(solid.Ws)", "intLN(u^2)", "intLN(v^2)"
    });
    model.result().numerical("gevE").set("looplevelinput", new String[]{"all"});
    double[][] re = model.result().numerical("gevE").getReal();
    double[][] im = model.result().numerical("gevE").getImag();
    int n = re[0].length;
    double bestF = hintHz;
    double bestDist = 1e99;
    for (int m = 0; m < n; m++) {
      double f = re[0][m];
      double fi = im[0][m];
      double eL = Math.abs(re[1][m]);
      double eA = Math.abs(re[2][m]);
      double u2 = Math.abs(re[3][m]);
      double v2 = Math.abs(re[4][m]);
      double et = eL + eA;
      double ut = u2 + v2;
      double pv = ut > 0 ? v2 / ut : 0;
      double frac = et > 0 ? eL / et : 0;
      System.out.println(String.format(java.util.Locale.US,
          "EIG f_GHz=%.6f fi_MHz=%.3f fracLN=%.4f pu=%.3f pv=%.3f",
          f / 1e9, fi / 1e6, frac, ut > 0 ? u2 / ut : -1, pv));
      if (pv < 0.85 || frac < 0.93) continue;
      double dist = Math.abs(f - hintHz);
      if (dist < bestDist) {
        bestDist = dist;
        bestF = f;
      }
    }
    System.out.println(String.format(java.util.Locale.US,
        "PICK f_GHz=%.6f hint_GHz=%.3f", bestF / 1e9, hintHz / 1e9));
    return bestF;
  }

  static void drive(Model model, double f0, double neffTE, double ngTE, double gTE,
                     double neffTM, double ngTM, double gTM) {
    model.physics("es").feature().remove("gndT");
    model.physics("es").create("term1", "Terminal", 1);
    model.physics("es").feature("term1").selection().named("selTerm");
    model.physics("es").feature("term1").set("TerminalType", "Voltage");
    model.physics("es").feature("term1").set("V0", "1");
    System.out.println("Nterm " + model.component("comp1").selection("selTerm").entities().length
        + " Ngnd " + model.component("comp1").selection("selGn").entities().length);

    double q = 2000;
    double[] scale = {-3, -1, 0, 1, 3};
    StringBuilder plist = new StringBuilder();
    for (int i = 0; i < scale.length; i++) {
      if (i > 0) plist.append(", ");
      double f = f0 * (1.0 + scale[i] / q);
      plist.append(String.format(java.util.Locale.US, "%.8e[Hz]", f));
    }
    model.study().create("stdF");
    model.study("stdF").create("fr", "Frequency");
    model.study("stdF").feature("fr").set("plist", plist.toString());
    model.study("stdF").createAutoSequences("all");
    model.study("stdF").run();

    model.result().numerical().create("gevF", "EvalGlobal");
    String[] ds = model.result().dataset().tags();
    String last = ds[ds.length - 1];
    System.out.println("DATA " + last);
    model.result().numerical("gevF").set("data", last);
    model.result().numerical("gevF").set("expr", new String[]{
      "freq", "intLN(1)", "intLN(wTE)", "intLN(wTM)",
      "real(intLN(dnZ))", "imag(intLN(dnZ))",
      "real(intLN(dnZ*wTE))", "imag(intLN(dnZ*wTE))",
      "real(intLN(dnX))", "imag(intLN(dnX))",
      "real(intLN(dnX*wTM))", "imag(intLN(dnX*wTM))",
      "intLN(real(v)^2+imag(v)^2)",
      "real(intLN(v))", "imag(intLN(v))",
      "mx(sqrt(real(v)^2+imag(v)^2))",
      "mx(sqrt(real(S1)^2+imag(S1)^2))",
      "mx(sqrt(real(S2)^2+imag(S2)^2))",
      "mx(abs(V))"
    });
    model.result().numerical("gevF").set("looplevelinput", new String[]{"all"});
    double[][] re = model.result().numerical("gevF").getReal();
    int n = re[0].length;
    int iBest = 0;
    double bestDn = -1;
    for (int m = 0; m < n; m++) {
      double area = re[1][m];
      double wte = re[2][m];
      double dnRe = re[6][m] / wte;
      double dnIm = re[7][m] / wte;
      double dne = (NE / neffTE) * gTE * Math.hypot(dnRe, dnIm);
      double df = dne * FOPT * LA / (ngTE * LRING);
      double rmsV = Math.sqrt(re[12][m] / area);
      double meanV = Math.hypot(re[13][m], re[14][m]) / area;
      System.out.println(String.format(java.util.Locale.US,
          "FD f_GHz=%.6f Vmax=%.4f vmax_pm=%.4f vrms_pm=%.4f vmean_pm=%.4f S1pk=%.4e S2pk=%.4e dfTE_GHz=%.6f",
          re[0][m] / 1e9, re[18][m], re[15][m] * 1e12, rmsV * 1e12, meanV * 1e12,
          re[16][m], re[17][m], df / 1e9));
      if (dne > bestDn) {
        bestDn = dne;
        iBest = m;
      }
    }
    reportPoint(re, iBest, neffTE, ngTE, gTE, neffTM, ngTM, gTM, "PEAK");
    int i0 = 0;
    double dmin = 1e99;
    for (int m = 0; m < n; m++) {
      double d = Math.abs(re[0][m] - f0);
      if (d < dmin) {
        dmin = d;
        i0 = m;
      }
    }
    if (i0 != iBest) reportPoint(re, i0, neffTE, ngTE, gTE, neffTM, ngTM, gTM, "AT_EIG");
  }

  static void reportPoint(double[][] re, int m, double neffTE, double ngTE, double gTE,
                          double neffTM, double ngTM, double gTM, String tag) {
    double area = re[1][m];
    double wte = re[2][m];
    double wtm = re[3][m];
    double zRe = re[6][m] / wte;
    double zIm = re[7][m] / wte;
    double xRe = re[10][m] / wtm;
    double xIm = re[11][m] / wtm;
    double dneTE = (NE / neffTE) * gTE * Math.hypot(zRe, zIm);
    double dneTM = (NO / neffTM) * gTM * Math.hypot(xRe, xIm);
    double dfTE = dneTE * FOPT * LA / (ngTE * LRING);
    double dfTE23 = dneTE * FOPT * LA / (2.3 * LRING);
    double dfTM = dneTM * FOPT * LA / (ngTM * LRING);
    double meanZ = Math.hypot(re[4][m], re[5][m]) / area;
    System.out.println(String.format(java.util.Locale.US,
        "RESULT %s f_GHz=%.6f mean|dnZ|=%.6e w|dnZ|=%.6e dneffTE=%.6e dfTE_GHz=%.6f dfTE_ng2.3_GHz=%.6f xiTE=%.6f xiTE_ng2.3=%.6f dfTM_GHz=%.6f xiTM=%.6f S1pk=%.6e S2pk=%.6e",
        tag, re[0][m] / 1e9, meanZ, Math.hypot(zRe, zIm), dneTE,
        dfTE / 1e9, dfTE23 / 1e9, (dfTE / 1e9) / GHzV, (dfTE23 / 1e9) / GHzV,
        dfTM / 1e9, (dfTM / 1e9) / GHzV, re[16][m], re[17][m]));
  }
}
