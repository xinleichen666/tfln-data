import com.comsol.model.*;
import com.comsol.model.util.*;

/**
 * Non-suspended 2D IDT unit cell. Find k at 3.33 GHz.
 * X-cut: in-plane rotation 90 deg so crystal X is the wafer normal
 * and crystal Y is opposite the propagation direction. Crystal Z is out of plane.
 * Both electrodes are grounded (shorted grating). Eigenfrequency, not a 1 V drive.
 */
public class Idt2d {
  static final String PZ = "D:\\COMSOL63\\Multiphysics\\data\\comsol_piezo_lib.mph";
  static final String BASIC = "D:\\COMSOL63\\Multiphysics\\data\\comsol_basic_material_lib.mph";
  static final String MEMS = "D:\\COMSOL63\\Multiphysics\\data\\comsol_mems_lib.mph";

  public static void main(String[] args) throws Exception {
    ModelUtil.initStandalone(true);
    Model model = ModelUtil.create("Model");
    model.modelPath("D:\\comsol_ao_run\\idt_2d");
    model.label("idt_2d.mph");
    try {
      build(model);
      double[] periods = {0.94};
      double[] als = {100};
      for (int j = 0; j < als.length; j++) {
        for (int i = 0; i < periods.length; i++) {
          solve(model, periods[i], als[j]);
        }
      }
    } catch (Throwable ex) {
      ex.printStackTrace(System.out);
    }
  }

  static void copyGroup(Material dst, Material src, String group, boolean create) {
    if (create) {
      dst.propertyGroup().create(group, group);
    }
    String[] names = src.propertyGroup(group).properties();
    for (int i = 0; i < names.length; i++) {
      try {
        String[] v = src.propertyGroup(group).getStringArray(names[i]);
        dst.propertyGroup(group).set(names[i], v);
      } catch (Exception ex) {
        System.out.println("skip " + group + "." + names[i] + " " + ex.getMessage());
      }
    }
  }

  static void build(Model model) throws Exception {
    model.param().set("p", "1[um]");
    model.param().set("hSi", "12[um]");
    model.param().set("hOx", "1[um]");
    model.param().set("hLn", "500[nm]");
    model.param().set("hAl", "100[nm]");
    model.param().set("duty", "0.25");

    model.modelNode().create("comp1");
    model.geom().create("geom1", 2);
    model.geom("geom1").lengthUnit("m");

    model.component("comp1").coordSystem().create("rot1", "Rotated");
    model.component("comp1").coordSystem("rot1").set("inPlaneAngle", "90[deg]");

    String[][] rects = {
      {"rSi", "p", "hSi", "0", "0"},
      {"rOx", "p", "hOx", "0", "hSi"},
      {"rLn", "p", "hLn", "0", "hSi+hOx"},
      {"rAp", "duty*p", "hAl", "(p-2*duty*p)/4", "hSi+hOx+hLn"},
      {"rAn", "duty*p", "hAl", "p/2+(p-2*duty*p)/4", "hSi+hOx+hLn"}
    };
    for (int i = 0; i < rects.length; i++) {
      model.geom("geom1").feature().create(rects[i][0], "Rectangle");
      model.geom("geom1").feature(rects[i][0]).set("size", new String[]{rects[i][1], rects[i][2]});
      model.geom("geom1").feature(rects[i][0]).set("pos", new String[]{rects[i][3], rects[i][4]});
    }
    model.geom("geom1").run();

    box(model, "selSi", 2, "1[nm]", "p-1[nm]", "1[nm]", "hSi-1[nm]");
    box(model, "selOx", 2, "1[nm]", "p-1[nm]", "hSi+1[nm]", "hSi+hOx-1[nm]");
    box(model, "selLN", 2, "1[nm]", "p-1[nm]", "hSi+hOx+1[nm]", "hSi+hOx+hLn-1[nm]");
    box(model, "selAl", 2, "1[nm]", "p-1[nm]", "hSi+hOx+hLn+1[nm]", "hSi+hOx+hLn+hAl-1[nm]");
    box(model, "selBot", 1, "-1[nm]", "p+1[nm]", "-1[nm]", "1[nm]");
    box(model, "selLeft", 1, "-0.5[nm]", "0.5[nm]", "2[nm]", "hSi+hOx+hLn+hAl-2[nm]");
    box(model, "selRight", 1, "p-0.5[nm]", "p+0.5[nm]", "2[nm]", "hSi+hOx+hLn+hAl-2[nm]");
    box(model, "selLeftE", 1, "-0.5[nm]", "0.5[nm]", "hSi+hOx+1[nm]", "hSi+hOx+hLn-1[nm]");
    box(model, "selRightE", 1, "p-0.5[nm]", "p+0.5[nm]", "hSi+hOx+1[nm]", "hSi+hOx+hLn-1[nm]");
    box(model, "selGp", 1, "(p-2*duty*p)/4-1[nm]", "(p-2*duty*p)/4+duty*p+1[nm]",
        "hSi+hOx+hLn-1[nm]", "hSi+hOx+hLn+1[nm]");
    box(model, "selGn", 1, "p/2+(p-2*duty*p)/4-1[nm]", "p/2+(p-2*duty*p)/4+duty*p+1[nm]",
        "hSi+hOx+hLn-1[nm]", "hSi+hOx+hLn+1[nm]");
    model.component("comp1").selection().create("selGnd", "Union");
    model.component("comp1").selection("selGnd").set("entitydim", "1");
    model.component("comp1").selection("selGnd").set("input", new String[]{"selGp", "selGn"});
    model.component("comp1").selection().create("selPer", "Union");
    model.component("comp1").selection("selPer").set("entitydim", "1");
    model.component("comp1").selection("selPer").set("input", new String[]{"selLeft", "selRight"});
    model.component("comp1").selection().create("selPerE", "Union");
    model.component("comp1").selection("selPerE").set("entitydim", "1");
    model.component("comp1").selection("selPerE").set("input", new String[]{"selLeftE", "selRightE"});

    Model pz = ModelUtil.load("pz", PZ);
    Model basic = ModelUtil.load("basic", BASIC);
    Model mems = ModelUtil.load("mems", MEMS);

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

    Material ox = model.component("comp1").material().create("matOx", "Common");
    ox.label("SiO2");
    ox.selection().named("selOx");
    copyGroup(ox, mems.material("sio2_-_silicon_oxide"), "def", false);
    copyGroup(ox, mems.material("sio2_-_silicon_oxide"), "Enu", true);

    Material si = model.component("comp1").material().create("matSi", "Common");
    si.label("Silicon");
    si.selection().named("selSi");
    copyGroup(si, basic.material("silicon"), "def", false);
    copyGroup(si, basic.material("silicon"), "Enu", true);

    ModelUtil.remove("pz");
    ModelUtil.remove("basic");
    ModelUtil.remove("mems");

    model.physics().create("solid", "SolidMechanics", "geom1");
    model.physics().create("es", "Electrostatics", "geom1");
    model.physics("es").selection().named("selLN");
    model.multiphysics().create("pze1", "PiezoelectricEffect", "geom1");

    String[] ptypes = {"PiezoelectricMaterialModel", "PiezoelectricModel", "PiezoelectricMaterial"};
    boolean made = false;
    for (int i = 0; i < ptypes.length && !made; i++) {
      try {
        model.physics("solid").create("pzm1", ptypes[i], 2);
        model.physics("solid").feature("pzm1").selection().named("selLN");
        System.out.println("PZM_OK " + ptypes[i]);
        made = true;
      } catch (Exception ex) {
        System.out.println("PZM_NO " + ptypes[i] + " " + ex.getMessage());
        try { model.physics("solid").feature().remove("pzm1"); } catch (Exception e2) {}
      }
    }
    if (!made) throw new RuntimeException("no piezoelectric material feature");
    model.physics("solid").create("fix1", "Fixed", 1);
    model.physics("solid").feature("fix1").selection().named("selBot");
    model.physics("solid").create("pc1", "PeriodicCondition", 1);
    model.physics("es").create("gnd1", "Ground", 1);
    model.physics("es").feature("gnd1").selection().named("selGnd");
    model.physics("es").create("pc1", "PeriodicCondition", 1);
    applyPeriodic(model);

    String[] ops = {"intLN", "intOx", "intSi", "intAl"};
    String[] sels = {"selLN", "selOx", "selSi", "selAl"};
    for (int i = 0; i < ops.length; i++) {
      model.component("comp1").cpl().create(ops[i], "Integration");
      model.component("comp1").cpl(ops[i]).selection().geom("geom1", 2);
      model.component("comp1").cpl(ops[i]).selection().named(sels[i]);
    }

    model.mesh().create("mesh1", "geom1");
    size(model, "szLN", "selLN", "40[nm]", "8[nm]");
    size(model, "szAl", "selAl", "40[nm]", "8[nm]");
    size(model, "szOx", "selOx", "200[nm]", "40[nm]");
    size(model, "szSi", "selSi", "1.5[um]", "200[nm]");
    model.mesh("mesh1").feature().create("ftri1", "FreeTri");
    model.mesh("mesh1").feature("ftri1").selection().geom("geom1", 2);
    model.mesh("mesh1").feature("ftri1").selection().all();
    model.mesh("mesh1").run();

    model.study().create("std1");
    model.study("std1").create("eig", "Eigenfrequency");
    model.study("std1").feature("eig").set("neigs", "8");
    model.study("std1").feature("eig").set("shift", "3.33[GHz]");
    model.study("std1").feature("eig").set("shiftactive", "on");
    model.study("std1").createAutoSequences("all");
    System.out.println("BUILD_OK");
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
      boolean vertical = Math.abs(x0 - x1) < 1e-10 && Math.abs(y0 - y1) > 1e-10;
      if (!vertical) continue;
      double ylo = Math.min(y0, y1);
      double yhi = Math.max(y0, y1);
      if (lnOnly && (ylo < 13.0e-6 - 1e-9 || yhi > 13.5e-6 + 1e-9)) continue;
      if (Math.abs(x0) < 1e-9) left[nl++] = e;
      if (Math.abs(x0 - pmax) < 1e-9 || Math.abs(x1 - pmax) < 1e-9) right[nr++] = e;
    }
    int[] use = new int[nl + nr];
    System.arraycopy(left, 0, use, 0, nl);
    System.arraycopy(right, 0, use, nl, nr);
    return use;
  }

  static void applyPeriodic(Model model) {
    int[] solid = sideEdges(model, false);
    int[] es = sideEdges(model, true);
    System.out.println("VERT solid=" + solid.length + " es=" + es.length);
    model.physics("solid").feature("pc1").selection().set(solid);
    model.physics("es").feature("pc1").selection().set(es);
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

  static void size(Model model, String tag, String sel, String hmax, String hmin) {
    model.mesh("mesh1").feature().create(tag, "Size");
    model.mesh("mesh1").feature(tag).selection().geom("geom1", 2);
    model.mesh("mesh1").feature(tag).selection().named(sel);
    model.mesh("mesh1").feature(tag).set("hmaxactive", "on");
    model.mesh("mesh1").feature(tag).set("hminactive", "on");
    model.mesh("mesh1").feature(tag).set("hmax", hmax);
    model.mesh("mesh1").feature(tag).set("hmin", hmin);
  }

  static void solve(Model model, double pUm, double hAlNm) {
    System.out.println("SOLVE p_um=" + pUm + " hAl_nm=" + hAlNm);
    try {
      model.param().set("p", pUm + "[um]");
      model.param().set("hAl", hAlNm + "[nm]");
      model.geom("geom1").run();
      applyPeriodic(model);
      model.component("comp1").cpl("intLN").selection().named("selLN");
      model.component("comp1").cpl("intOx").selection().named("selOx");
      model.component("comp1").cpl("intSi").selection().named("selSi");
      model.component("comp1").cpl("intAl").selection().named("selAl");
      model.mesh("mesh1").run();
      model.study("std1").run();
      if (model.result().numerical().tags().length > 0) {
        try { model.result().numerical().remove("gev1"); } catch (Exception ex) { }
      }
      model.result().numerical().create("gev1", "EvalGlobal");
      model.result().numerical("gev1").set("expr", new String[]{
        "freq", "intLN(solid.Ws)", "intOx(solid.Ws)", "intSi(solid.Ws)", "intAl(solid.Ws)"
      });
      model.result().numerical("gev1").set("looplevelinput", new String[]{"all"});
      double[][] re = model.result().numerical("gev1").getReal();
      System.out.println("SHAPE rows=" + re.length + " cols=" + (re.length > 0 ? re[0].length : 0));
      int n = re[0].length;
      int rows = re.length;
      if (rows >= 5 && n < rows) {
        // layout is expr x mode or mode x expr; detect by freq magnitude
      }
      boolean freqIsRow = Math.abs(re[0][0]) > 1e6;
      int nMode = freqIsRow ? re[0].length : re.length;
      for (int m = 0; m < nMode; m++) {
        double f = freqIsRow ? re[0][m] : re[m][0];
        double eL = freqIsRow ? re[1][m] : re[m][1];
        double eO = freqIsRow ? re[2][m] : re[m][2];
        double eS = freqIsRow ? re[3][m] : re[m][3];
        double eA = freqIsRow ? re[4][m] : re[m][4];
        double tot = Math.abs(eL) + Math.abs(eO) + Math.abs(eS) + Math.abs(eA);
        double k = 2 * Math.PI / (pUm * 1e-6);
        System.out.println(String.format(java.util.Locale.US,
            "ROW p_um=%.4f hAl_nm=%.1f f_GHz=%.6f k_rad_m=%.6e fracLN=%.4f fracOx=%.4f fracSi=%.4f fracAl=%.4f",
            pUm, hAlNm, f / 1e9, k, tot > 0 ? Math.abs(eL) / tot : -1,
            tot > 0 ? Math.abs(eO) / tot : -1, tot > 0 ? Math.abs(eS) / tot : -1,
            tot > 0 ? Math.abs(eA) / tot : -1));
      }
    } catch (Throwable ex) {
      System.out.println("FAIL p_um=" + pUm);
      ex.printStackTrace(System.out);
    }
  }
}
