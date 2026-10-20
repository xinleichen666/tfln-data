import com.comsol.model.*;
import com.comsol.model.util.*;

/** Window the existing 1 V solution along x. Flat film, no new solve. */
public class Sweep {
  static final double NE = 2.138;
  static final double NEFF = 1.88978;
  static final double GAMMA = 0.8933;
  static final double NG = 2.21727;
  static final double LA = 100e-6;
  static final double LRING = 0.667e-3;
  static final double FOPT = 193.4e12;

  public static void main(String[] args) throws Exception {
    ModelUtil.initStandalone(true);
    Model m = ModelUtil.load("Model", "D:\\comsol_ao_run\\photoelastic\\Photo_Model.mph");
    String[] ds = m.result().dataset().tags();
    System.out.println("NDATA " + ds.length + " LAST " + ds[ds.length - 1]);
    m.result().numerical().create("gf", "EvalGlobal");
    m.result().numerical("gf").set("data", ds[ds.length - 1]);
    m.result().numerical("gf").set("expr", new String[]{"freq", "mx(abs(V))"});
    m.result().numerical("gf").set("looplevelinput", new String[]{"all"});
    double[][] fr = m.result().numerical("gf").getReal();
    int nSol = fr[0].length;
    int i0 = 0;
    double best = 1e99;
    for (int i = 0; i < nSol; i++) {
      System.out.println(String.format(java.util.Locale.US,
          "SOL %d f_GHz=%.6f Vmax=%.4f", i, fr[0][i] / 1e9, fr[1][i]));
      double d = Math.abs(fr[0][i] - 3.330092e9);
      if (d < best) { best = d; i0 = i; }
    }
    double p = m.param().evaluate("p");
    System.out.println(String.format(java.util.Locale.US, "P_UM %.4f ISOL %d", p * 1e6, i0));
    double[] widths = {0.50e-6, 0.95e-6, 1.30e-6, p / 2};
    double bestDf = -1;
    String bestTag = "";
    for (int w = 0; w < widths.length; w++) {
      double width = widths[w];
      int npos = 8;
      for (int k = 0; k < npos; k++) {
        double xa = (p - width) * k / (npos - 1.0);
        double xb = xa + width;
        String win = "(x>" + xa + ")*(x<" + xb + ")";
        String tag = "w" + w + "k" + k;
        m.result().numerical().create(tag, "EvalGlobal");
        m.result().numerical(tag).set("data", ds[ds.length - 1]);
        m.result().numerical(tag).set("looplevelinput", new String[]{"all"});
        m.result().numerical(tag).set("expr", new String[]{
          "real(intLN(dnZ*" + win + "))",
          "imag(intLN(dnZ*" + win + "))",
          "real(intLN(dnZ*wTE*" + win + "))",
          "imag(intLN(dnZ*wTE*" + win + "))",
          "intLN(wTE*" + win + ")"
        });
        double[][] re = m.result().numerical(tag).getReal();
        double wt = re[4][i0];
        if (Math.abs(wt) < 1e-30) continue;
        double dn = Math.hypot(re[2][i0], re[3][i0]) / wt;
        double dne = (NE / NEFF) * GAMMA * dn;
        double df = dne * FOPT * LA / (NG * LRING);
        double df23 = dne * FOPT * LA / (2.3 * LRING);
        System.out.println(String.format(java.util.Locale.US,
            "WIN w_um=%.3f x0_um=%.3f df_GHz=%.4f df23_GHz=%.4f xi=%.4f",
            width * 1e6, xa * 1e6, df / 1e9, df23 / 1e9, (df / 1e9) / 21.3));
        if (df > bestDf) {
          bestDf = df;
          bestTag = String.format(java.util.Locale.US,
              "BEST w_um=%.3f x0_um=%.3f df_GHz=%.4f df23_GHz=%.4f xi=%.4f",
              width * 1e6, xa * 1e6, df / 1e9, df23 / 1e9, (df / 1e9) / 21.3);
        }
      }
    }
    System.out.println(bestTag);
  }
}
