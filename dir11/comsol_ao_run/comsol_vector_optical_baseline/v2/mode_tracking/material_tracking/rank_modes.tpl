import com.comsol.model.*;
import com.comsol.model.util.*;

/**
 * Rank every stored mode of one model against an embedded reference field.
 *
 * The reference field and the area weights are compiled into the class, so a
 * single run yields the overlap of all modes with it.  Evaluating 40 modes by
 * launching 40 separate runs would cost 40 model loads for the same numbers.
 *
 * S is the area-weighted conjugated overlap; both the real and imaginary parts
 * of the normalised overlap are printed, so a phase change cannot hide inside
 * an absolute value.
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

  public static void main(String[] args) throws Exception {
    ModelUtil.initStandalone(true);
    double[] x = join(__XJOIN__);
    double[] y = join(__YJOIN__);
    double[] w = join(__WJOIN__);
    double[] rr = join(__RRJOIN__), ri = join(__RIJOIN__);
    double[] gr = join(__GRJOIN__), gi = join(__GIJOIN__);
    double[] br = join(__BRJOIN__), bi = join(__BIJOIN__);
    int n = x.length;
    System.out.println("NPOINTS " + n);

    double nref = 0.0;
    for (int p = 0; p < n; p++) {
      nref += w[p] * (rr[p]*rr[p] + ri[p]*ri[p] + gr[p]*gr[p]
                    + gi[p]*gi[p] + br[p]*br[p] + bi[p]*bi[p]);
    }
    System.out.println(String.format(java.util.Locale.US, "NREF %.17g", nref));

    Model m = ModelUtil.load("m", "__MODEL__");
    System.out.println("LOADED __MODEL__");
    m.result().numerical().create("rk", "Interp");
    m.result().numerical("rk").set("data", "dset1");
    m.result().numerical("rk").set("coord", new double[][]{x, y});
    m.result().numerical("rk").set("coorderr", "on");
    m.result().numerical("rk").set("ext", 0.0);
    m.result().numerical("rk").set("expr", new String[]{
        "real(ewfd.Ex)", "imag(ewfd.Ex)",
        "real(ewfd.Ey)", "imag(ewfd.Ey)",
        "real(ewfd.Ez)", "imag(ewfd.Ez)"});

    for (int s = 1; s <= __NMODE__; s++) {
      m.result().numerical("rk").set("solnum", new int[]{s});
      m.result().numerical("rk").run();
      double[][][] d = m.result().numerical("rk").getData();
      if (d.length != 6 || d[0][0].length != n) {
        System.out.println("SHAPE_BAD " + s);
        continue;
      }
      double ir = 0.0, ii = 0.0, nn = 0.0;
      for (int p = 0; p < n; p++) {
        double ax = d[0][0][p], ay = d[1][0][p];
        double bx = d[2][0][p], by = d[3][0][p];
        double cx = d[4][0][p], cy = d[5][0][p];
        // conj(Eref) . E
        ir += w[p] * ((rr[p]*ax + ri[p]*ay) + (gr[p]*bx + gi[p]*by)
                    + (br[p]*cx + bi[p]*cy));
        ii += w[p] * ((rr[p]*ay - ri[p]*ax) + (gr[p]*by - gi[p]*bx)
                    + (br[p]*cy - bi[p]*cx));
        nn += w[p] * (ax*ax + ay*ay + bx*bx + by*by + cx*cx + cy*cy);
      }
      double den = Math.sqrt(nref * nn);
      double S = den > 0 ? Math.sqrt(ir*ir + ii*ii) / den : 0.0;
      System.out.println(String.format(java.util.Locale.US,
          "MODE %d S=%.9f zre=%.9f zim=%.9f nrm=%.12g",
          s, S, ir / den, ii / den, nn));
    }
    System.out.println("RANK_DONE");
    ModelUtil.disconnect();
  }
}
