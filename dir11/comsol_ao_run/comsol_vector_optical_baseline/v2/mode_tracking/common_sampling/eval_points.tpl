import com.comsol.model.*;
import com.comsol.model.util.*;

/**
 * Evaluate field quantities at chosen coordinates for ONE solution of a saved
 * model, at full double precision, and echo everything needed to validate the
 * data path:
 *
 *   x, y, dom, ewfd.normE,
 *   Ex re/im, Ey re/im, Ez re/im,
 *   sqrt(|Ex|^2+|Ey|^2+|Ez|^2)   computed INSIDE COMSOL
 *
 * No study is run; the saved solution is only evaluated.
 */
public class __CLASS__ {
  public static void main(String[] a) throws Exception {
    ModelUtil.initStandalone(true);
    Model m = ModelUtil.load("m", "__MODEL__");
    System.out.println("LOADED " + "__MODEL__");

    double[][] coord = __COORDS__;
    int solnum = __SOLNUM__;
    System.out.println("NPOINTS " + coord[0].length + " SOLNUM " + solnum);

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
    if (nexpr != 11 || nsol != 1) {
      System.out.println("SHAPE_UNEXPECTED");
    }
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
