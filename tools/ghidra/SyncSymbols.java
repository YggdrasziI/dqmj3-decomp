// Applies config/<version>/symbols.txt to the program: Thumb mode, functions, names.
// Run by tools/ghidra_sync.py (analyzeHeadless). Arguments: <symbols.txt> [dry]
//
// A real name of symbols.txt (not fn_<addr> / lbl_<addr>) replaces the name in
// Ghidra. An analysis name only replaces a default Ghidra name (FUN_..., DAT_...),
// so names typed in Ghidra are kept; they are listed, as they are not evidence.
//@category DQMJ3

import java.math.BigInteger;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.List;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.lang.Register;
import ghidra.program.model.listing.ContextChangeException;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionManager;
import ghidra.program.model.listing.ProgramContext;
import ghidra.program.model.symbol.SourceType;
import ghidra.program.model.symbol.Symbol;
import ghidra.program.model.symbol.SymbolTable;

public class SyncSymbols extends GhidraScript {

    private static final Pattern LINE =
        Pattern.compile("^(\\S+) = (\\.\\w+):0x([0-9A-Fa-f]+);\\s*//(.*)$");
    private static final Pattern SIZE = Pattern.compile("size:0x([0-9A-Fa-f]+)");
    private static final Pattern ANALYSIS = Pattern.compile("^(fn|lbl)_[0-9A-F]{8}$");

    private boolean dry;
    private int named, kept, created, thumb, thumbConflicts, labels;

    @Override
    public void run() throws Exception {
        String[] args = getScriptArgs();
        if (args.length < 1) {
            printerr("usage: SyncSymbols.java <symbols.txt> [dry]");
            return;
        }
        dry = args.length > 1 && args[1].equals("dry");
        List<String> lines = Files.readAllLines(Paths.get(args[0]), StandardCharsets.UTF_8);

        Register tmode = currentProgram.getRegister("TMode");
        ProgramContext context = currentProgram.getProgramContext();
        FunctionManager functions = currentProgram.getFunctionManager();
        SymbolTable table = currentProgram.getSymbolTable();

        // Thumb mode first, so that disassembly follows it
        for (String line : lines) {
            Matcher m = LINE.matcher(line);
            if (!m.matches() || !m.group(4).contains("mode:thumb")) {
                continue;
            }
            Address start = toAddr(Long.parseLong(m.group(3), 16));
            Address end = start.add(Math.max(size(m.group(4)), 2) - 1);
            BigInteger current = context.getValue(tmode, start, false);
            if (BigInteger.ONE.equals(current)) {
                continue;
            }
            if (!dry) {
                try {
                    context.setValue(tmode, start, end, BigInteger.ONE);
                } catch (ContextChangeException e) {
                    // Already disassembled as ARM: leave it, report it
                    thumbConflicts++;
                    println("warning: Thumb range conflicts with instructions at " + start);
                    continue;
                }
            }
            thumb++;
        }

        monitor.initialize(lines.size());
        for (String line : lines) {
            monitor.checkCancelled();
            monitor.incrementProgress(1);
            Matcher m = LINE.matcher(line);
            if (!m.matches()) {
                continue;
            }
            String name = m.group(1);
            Address addr = toAddr(Long.parseLong(m.group(3), 16));
            boolean isFunction = m.group(4).contains("type:function");
            if (isFunction) {
                Function f = functions.getFunctionAt(addr);
                if (f == null) {
                    created++;
                    if (dry) {
                        continue;
                    }
                    disassemble(addr);
                    f = createFunction(addr, name);
                    if (f == null) {
                        printerr("could not create a function at " + addr + " (" + name + ")");
                        continue;
                    }
                }
                apply(f.getSymbol(), name);
            } else {
                Symbol s = table.getPrimarySymbol(addr);
                if (s == null) {
                    labels++;
                    if (!dry) {
                        createLabel(addr, name, true, SourceType.IMPORTED);
                    }
                } else {
                    apply(s, name);
                }
            }
        }
        println(String.format("%s%d Thumb ranges set (%d conflicts), %d functions created, %d labels created, "
            + "%d names set, %d names typed in Ghidra kept", dry ? "(dry run) " : "", thumb, thumbConflicts,
            created, labels, named, kept));
    }

    private void apply(Symbol s, String name) throws Exception {
        if (s.getName().equals(name)) {
            return;
        }
        // Already there as a secondary symbol: Ghidra's demangler made a readable
        // primary name from it; keep that one
        for (Symbol other : currentProgram.getSymbolTable().getSymbols(s.getAddress())) {
            if (other.getName().equals(name)) {
                return;
            }
        }
        boolean real = !ANALYSIS.matcher(name).matches();
        boolean ghidraDefault = s.getSource() == SourceType.DEFAULT
            || ANALYSIS.matcher(s.getName()).matches();
        if (!real && !ghidraDefault) {
            kept++;
            println("kept Ghidra name " + s.getName() + " at " + s.getAddress() + " (symbols.txt: " + name + ")");
            return;
        }
        if (real && !ghidraDefault) {
            println("replaced Ghidra name " + s.getName() + " at " + s.getAddress() + " with " + name);
        }
        named++;
        if (!dry) {
            s.setName(name, SourceType.IMPORTED);
        }
    }

    private static long size(String rest) {
        Matcher m = SIZE.matcher(rest);
        return m.find() ? Long.parseLong(m.group(1), 16) : 0;
    }
}
