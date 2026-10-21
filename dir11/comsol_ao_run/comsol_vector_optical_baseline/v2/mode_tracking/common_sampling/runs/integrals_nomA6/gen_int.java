import com.comsol.model.*;
import com.comsol.model.util.*;
import java.util.*;

/**
 * High-precision reference integrals for ONE saved mode.
 *
 * Integrals are taken over real geometric domains, not over rectangular
 * footprints: in the no-metal model the electrode footprints are part of the
 * single air domain, so a box selection would silently integrate the whole of
 * air.  Each domain gets its own Explicit selection and its own Integration
 * operator, and the domain ids are printed so the Python side maps them to
 * sampling regions using the model's own numbering.
 *
 * Nothing is solved and nothing is saved.
 */
public class gen_int {

  static final String[] Q = new String[]{
      "ewfd.normE^2", "abs(ewfd.Ex)^2", "abs(ewfd.Ey)^2", "abs(ewfd.Ez)^2", "1"};

  public static void main(String[] args) throws Exception {
    ModelUtil.initStandalone(true);
    Model m = ModelUtil.load("m", "D:/comsol_ao_run/comsol_vector_optical_baseline/v2/out/final_nomA6.mph");
    System.out.println("LOADED " + "D:/comsol_ao_run/comsol_vector_optical_baseline/v2/out/final_nomA6.mph");
    int solnum = 40;

    ModelNode c = m.component("comp1");
    int nd = c.geom("geom1").getNDomains();
    System.out.println("NDOMAINS " + nd);

    // the model already carries one named selection per region (they were
    // used to assign materials), and each of them coincides with a domain, so
    // no new selection API has to be guessed
    String[] SELS = new String[]{"selAir", "selSlabL", "selRidge", "selSlabR",
                                 "selAlL", "selAlR"};
    List<String> used = new ArrayList<String>();
    List<String> ents = new ArrayList<String>();
    int k = 0;
    for (String s : SELS) {
      int[] got;
      try {
        got = c.selection(s).entities();
      } catch (Throwable t) {
        continue;                                  // selection not in this model
      }
      if (got == null || got.length == 0) continue;
      String it = "iv" + k;
      k++;
      m.result().numerical().create(it, "IntSurface");
      m.result().numerical(it).set("data", "dset1");
      try {
        m.result().numerical(it).selection().named(s);
      } catch (Throwable t) {
        m.result().numerical(it).set("selection", new String[]{s});
      }
      m.result().numerical(it).set("expr", Q);
      m.result().numerical(it).set("looplevelinput", new String[]{"manual"});
      m.result().numerical(it).set("looplevel",
          new String[]{Integer.toString(solnum)});
      used.add(s);
      ents.add(java.util.Arrays.toString(got));
      System.out.println("SEL " + s + " -> " + java.util.Arrays.toString(got)
                         + " op=" + it);
    }
    int nsel = used.size();

    // integration order must be checked, not assumed: an unstable quadrature
    // would make every comparison against this reference meaningless
    int[] ORDERS = new int[]{4, 6, 8};
    for (int oi = 0; oi < ORDERS.length; oi++) {
      int order = ORDERS[oi];
      System.out.println("ORDER_BEGIN " + order);
      for (int d = 0; d < nsel; d++) {
        String it = "iv" + d;
        boolean applied = false;
        try {
          m.result().numerical(it).set("intorderactive", true);
          m.result().numerical(it).set("intorder", order);
          applied = true;
        } catch (Throwable t) {
          applied = false;
        }
        String readback = "?";
        try {
          readback = Integer.toString(m.result().numerical(it).getInt("intorder"));
        } catch (Throwable t) {
          try {
            readback = m.result().numerical(it).getString("intorder");
          } catch (Throwable t2) { readback = "UNREADABLE"; }
        }
        double[][] vv = m.result().numerical(it).getReal();
        StringBuilder sb = new StringBuilder("ORD " + order + " "
            + used.get(d) + " applied=" + applied + " readback=" + readback);
        for (int q = 0; q < Q.length; q++) {
          sb.append(String.format(java.util.Locale.US, " %.17g", vv[q][0]));
        }
        System.out.println(sb.toString());
      }
    }

    m.result().numerical().create("gn", "EvalGlobal");
    m.result().numerical("gn").set("data", "dset1");
    m.result().numerical("gn").set("expr",
        new String[]{"real(ewfd.neff)", "imag(ewfd.neff)"});
    m.result().numerical("gn").set("looplevelinput", new String[]{"manual"});
    m.result().numerical("gn").set("looplevel",
        new String[]{Integer.toString(solnum)});
    double[][] nv = m.result().numerical("gn").getReal();
    System.out.println(String.format(java.util.Locale.US,
        "MODENEFF sol=%d re=%.17g im=%.17g", solnum, nv[0][0], nv[1][0]));

    System.out.println("INTEGRALS_DONE");
    ModelUtil.disconnect();
  }
}
