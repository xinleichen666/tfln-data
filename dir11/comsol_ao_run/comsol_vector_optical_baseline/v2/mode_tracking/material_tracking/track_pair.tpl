import com.comsol.model.*;
import com.comsol.model.util.*;

/**
 * Rank every mode of a target model against ONE mode of a reference model.
 *
 * Both are evaluated at the same compiled-in coordinates, so the comparison is
 * like for like.  The reference field is measured at run time instead of being
 * embedded, which keeps the source small and lets any step be used as the
 * reference.
 */
public class __CLASS__ {

  static double[] join(double[]... parts) {
    int n = 0;
    for (double[] p : parts) n += p.length;
    double[] out = new double[n];
    int k = 0;
    for (double[] p : parts) {
      System.arraycopy(p, 0, out, k, p.length);
      k += p.length;
    }
    return out;
  }

__CHUNKS__

  /** Evaluate one solution at the compiled coordinates: [6][n] re/im per comp. */
  static double[][] eval(Model m, int solnum, double[][] coord, int n) {
    m.result().numerical().create("pp", "Interp");
    m.result().numerical("pp").set("data", "dset1");
    m.result().numerical("pp").set("solnum", new int[]{solnum});
    m.result().numerical("pp").set("coord", coord);
    m.result().numerical("pp").set("coorderr", "on");
    m.result().numerical("pp").set("ext", 0.0);
    m.result().numerical("pp").set("expr", new String[]{
        "real(ewfd.Ex)", "imag(ewfd.Ex)",
        "real(ewfd.Ey)", "imag(ewfd.Ey)",
        "real(ewfd.Ez)", "imag(ewfd.Ez)"});
    m.result().numerical("pp").run();
    double[][][] d = m.result().numerical("pp").getData();
    double[][] out = new double[6][n];
    for (int e = 0; e < 6; e++) {
      for (int p = 0; p < n; p++) out[e][p] = d[e][0][p];
    }
    m.result().numerical().remove("pp");
    return out;
  }

  public static void main(String[] args) throws Exception {
    ModelUtil.initStandalone(true);
    double[] x = join(__XJOIN__);
    double[] y = join(__YJOIN__);
    double[] w = join(__WJOIN__);
    int n = x.length;
    double[][] coord = new double[][]{x, y};
    System.out.println("NPOINTS " + n);

    Model mr = ModelUtil.load("mr", "__REFMODEL__");
    double[][] R = eval(mr, __REFSOL__, coord, n);
    double nref = 0.0;
    for (int p = 0; p < n; p++) {
      nref += w[p] * (R[0][p]*R[0][p] + R[1][p]*R[1][p]
                    + R[2][p]*R[2][p] + R[3][p]*R[3][p]
                    + R[4][p]*R[4][p] + R[5][p]*R[5][p]);
    }
    System.out.println(String.format(java.util.Locale.US, "NREF %.17g", nref));
    ModelUtil.disconnect();
    ModelUtil.initStandalone(true);

    Model mt = ModelUtil.load("mt", "__TGTMODEL__");
    for (int s = 1; s <= __NMODE__; s++) {
      double[][] E = eval(mt, s, coord, n);
      double ir = 0.0, ii = 0.0, nn = 0.0;
      for (int p = 0; p < n; p++) {
        double ax = E[0][p], ay = E[1][p];
        double bx = E[2][p], by = E[3][p];
        double cx = E[4][p], cy = E[5][p];
        ir += w[p] * ((R[0][p]*ax + R[1][p]*ay) + (R[2][p]*bx + R[3][p]*by)
                    + (R[4][p]*cx + R[5][p]*cy));
        ii += w[p] * ((R[0][p]*ay - R[1][p]*ax) + (R[2][p]*by - R[3][p]*bx)
                    + (R[4][p]*cy - R[5][p]*cx));
        nn += w[p] * (ax*ax + ay*ay + bx*bx + by*by + cx*cx + cy*cy);
      }
      double den = Math.sqrt(nref * nn);
      double S = den > 0 ? Math.sqrt(ir*ir + ii*ii) / den : 0.0;
      System.out.println(String.format(java.util.Locale.US,
          "MODE %d S=%.9f zre=%.9f zim=%.9f nrm=%.12g",
          s, S, ir / den, ii / den, nn));
    }
    System.out.println("PAIR_DONE");
    ModelUtil.disconnect();
  }
}
