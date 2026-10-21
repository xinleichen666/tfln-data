import com.comsol.model.*;
import com.comsol.model.util.*;

/**
 * Same evaluation as eval_points.tpl, but the coordinates are produced by
 * several small static methods and concatenated.  A single method's array
 * initialiser hits the 64 kB bytecode limit at a few thousand points, and
 * COMSOL batch forbids reading a coordinate file from disk (its security
 * preference denies "read"), so the data has to stay in the class.
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

__XCHUNKS__

__YCHUNKS__

  public static void main(String[] a) throws Exception {
    ModelUtil.initStandalone(true);
    double[][] coord = new double[][]{
        join(__XJOIN__),
        join(__YJOIN__)};
    System.out.println("NPOINTS " + coord[0].length);

    Model m = ModelUtil.load("m", "__MODEL__");
    System.out.println("LOADED " + "__MODEL__");
    int solnum = __SOLNUM__;

    m.result().numerical().create("pt", "Interp");
    m.result().numerical("pt").set("data", "dset1");
    m.result().numerical("pt").set("solnum", new int[]{solnum});
    m.result().numerical("pt").set("coord", coord);
    m.result().numerical("pt").set("coorderr", "on");
    m.result().numerical("pt").set("ext", 0.0);
    m.result().numerical("pt").set("expr", new String[]{
        "x", "y", "dom", "ewfd.normE",
        "real(ewfd.Ex)", "imag(ewfd.Ex)",
        "real(ewfd.Ey)", "imag(ewfd.Ey)",
        "real(ewfd.Ez)", "imag(ewfd.Ez)",
        "sqrt(abs(ewfd.Ex)^2+abs(ewfd.Ey)^2+abs(ewfd.Ez)^2)"});
    m.result().numerical("pt").run();

    double[][][] re = m.result().numerical("pt").getData();
    int nexpr = re.length;
    int nsol = re[0].length;
    int npts = re[0][0].length;
    System.out.println("SHAPE expr=" + nexpr + " sol=" + nsol + " pts=" + npts);
    for (int p = 0; p < npts; p++) {
      StringBuilder sb = new StringBuilder("PT " + p);
      for (int e = 0; e < nexpr; e++) {
        sb.append(String.format(java.util.Locale.US, " %.17g", re[e][0][p]));
      }
      System.out.println(sb.toString());
    }

    m.result().numerical().create("nchk", "EvalGlobal");
    m.result().numerical("nchk").set("data", "dset1");
    m.result().numerical("nchk").set("expr",
        new String[]{"real(ewfd.neff)", "imag(ewfd.neff)"});
    m.result().numerical("nchk").set("looplevelinput", new String[]{"manual"});
    m.result().numerical("nchk").set("looplevel",
        new String[]{Integer.toString(solnum)});
    double[][] v = m.result().numerical("nchk").getReal();
    System.out.println(String.format(java.util.Locale.US,
        "MODENEFF sol=%d re=%.17g im=%.17g", solnum, v[0][0], v[1][0]));
    System.out.println("DONE");
    ModelUtil.disconnect();
  }
}
