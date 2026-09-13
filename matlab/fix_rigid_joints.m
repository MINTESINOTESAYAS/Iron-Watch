function fix_rigid_joints(mdl, mode, jointList)
% FIX_RIGID_JOINTS  Repair "everything is rigid" after smimport.
%
%   After smimport('Gearbox_Design.xml'), parts that should rotate can show
%   up welded (connected by Rigid Transform blocks) when their SolidWorks
%   mates were over-constrained or the component was Fixed. This helper:
%
%     fix_rigid_joints(mdl, 'list')
%       Prints every Rigid Transform block in the imported model together
%       with the two blocks it welds, and a heuristic tag:
%         [WELD-TO-CASING?]  joins something that looks like a fixed frame
%                            (casing/housing/ground/world) -> likely WRONG
%                            if the other side is a shaft/gear/handle
%         [internal bond   ] gear-to-shaft / handle-to-shaft -> usually RIGHT
%
%     fix_rigid_joints(mdl, 'fix', {'Rigid Transform17', 'X';
%                                   'Rigid Transform23', 'X'})
%       Replaces each listed Rigid Transform with a Revolute Joint, rewires
%       the same two frame connections, and tries to set the rotation axis
%       (second column: 'X','Y','Z','-X','-Y','-Z'; default 'Z').
%       Works on a COPY: saves <mdl>_fixed and leaves the original untouched.
%       If the axis cannot be set programmatically on your release, the
%       script prints exactly which block to double-click and what to set.
%
%   Requires: Simulink + Simscape Multibody (R2019b+; target R2025b).
%   See docs/FIX_RIGID_JOINTS.md for the full procedure.

if nargin < 2, mode = 'list'; end
if nargin < 3, jointList = {}; end

if ~bdIsLoaded(mdl)
    load_system(mdl);
end

% ---- find all Rigid Transform blocks (library-reference based) ----------
cands = cell(3, 1);
cands{1} = 'sm_lib/Frames/Rigid Transform';
cands{2} = 'sm_lib/Blocks/Rigid Transform';
cands{3} = 'sm_lib/Frames and Transforms/Rigid Transform';
rigids = {};
for c = 1:numel(cands)
    rigids = find_system(mdl, 'LookUnderMasks', 'all', ...
                         'ReferenceBlock', cands{c});
    if ~isempty(rigids), break; end
end
if isempty(rigids)   % fallback: by block name (covers renamed libraries)
    allb = find_system(mdl, 'LookUnderMasks', 'all', 'Type', 'Block');
    rigids = cell(0, 1);
    for k = 1:numel(allb)
        nm = get_param(allb{k}, 'Name');
        if ~isempty(strfind(nm, 'Rigid Transform'))
            nr = numel(rigids) + 1;
            rigids{nr, 1} = allb{k};
        end
    end
end

fprintf('Model "%s": found %d Rigid Transform block(s).\n', mdl, numel(rigids));

switch lower(mode)
    case 'list'
        for k = 1:numel(rigids)
            [b1, p1, b2, p2] = rigid_neighbors(rigids{k});
            fprintf('  %-28s welds %-30s (port %-3s) <-> %-30s (port %-3s)  %s\n', ...
                shortname(rigids{k}), shortname(b1), p1, shortname(b2), p2, ...
                classify(b1, b2));
        end
        fprintf('\nHeuristic: WELD-TO-CASING tag on a shaft/gear/handle block means that connection probably should be a REVOLUTE JOINT.\n');
        fprintf('Gear-to-shaft [internal bond] lines are correct as rigid.\n');
        fprintf('Fix with: fix_rigid_joints("%s", "fix", {"<name>", "<axis>"; ...})\n', mdl);

    case 'fix'
        newmdl = [mdl '_fixed'];
        if bdIsLoaded(newmdl), close_system(newmdl, 0); end
        save_system(mdl, newmdl);          % keep the original untouched
        fprintf('Working on copy: %s.slx (original untouched)\n', newmdl);
        for k = 1:size(jointList, 1)
            name = jointList{k, 1};
            if size(jointList, 2) > 1, axis = jointList{k, 2}; else, axis = 'Z'; end
            convert_one(newmdl, name, axis);
        end
        save_system(newmdl);
        fprintf('\nDONE. Next steps:\n');
        fprintf(' 1) Run the model once: Mechanics Explorer must report 4 DOF\n');
        fprintf('    (one Revolute per shaft unit: motor, A, B, output/arm).\n');
        fprintf(' 2) Verify that the Z axis of each new joint lies along its shaft (see\n');
        fprintf('    docs/FIX_RIGID_JOINTS.md section 5a step 5 if not).\n');
        fprintf(' 3) Add the 3 Gear Constraint blocks (SIMSCAPE_SOLIDWORKS_GUIDE.md Part 4).\n');
    otherwise
        error('mode must be list or fix');
end
end

%--------------------------------------------------------------------------
function [b1, p1, b2, p2] = rigid_neighbors(rblock)
% Block handles + port names of the two blocks welded by a Rigid Transform.
b1 = []; p1 = '?'; b2 = []; p2 = '?';
lh = get_param(rblock, 'LineHandles');
lines = [lh.lconn, lh.rconn];
for ln = lines
    if ln < 0, continue; end
    sp = get_param(ln, 'SrcPortHandle');
    dp = get_param(ln, 'DstPortHandle');
    if strcmp(get_param(sp, 'Parent'), rblock)
        otherP = dp; mineP = sp;
    else
        otherP = sp; mineP = dp;
    end
    if isempty(b1)
        b1 = get_param(otherP, 'Parent'); p1 = get_param(mineP, 'Name');
    else
        b2 = get_param(otherP, 'Parent'); p2 = get_param(mineP, 'Name');
    end
end
end

function tag = classify(b1, b2)
fixedish = 'casing|housing|ground|world|frame|base|mount';
n1 = shortname(b1);
n2 = shortname(b2);
a = ~isempty(regexpi(n1, fixedish, 'once'));
b = ~isempty(regexpi(n2, fixedish, 'once'));
if a || b
    tag = '[WELD-TO-CASING? -> should be REVOLUTE]';
else
    tag = '[internal bond -> usually correct]';
end
end

function s = shortname(h)
if isempty(h), s = '(open port)'; return; end
s = strrep(char(get_param(h, 'Name')), newline, ' ');
if numel(s) > 30, s = ['...' s(end-27:end)]; end
end

function convert_one(mdl, name, axis)
blk = [mdl '/' name];
h = getSimulinkBlockHandle(blk, true);
if h < 0
    error('Block "%s" not found in %s (run "list" mode for exact names).', name, mdl);
end
pos = get_param(h, 'Position');

% capture the two frame connections: {otherBlockHandle, otherPortHandle}
lh = get_param(h, 'LineHandles');
lines = [lh.lconn, lh.rconn];
endA = cell(1, 2);
endB = cell(1, 2);
slot = 0;
for ln = lines
    slot = slot + 1;
    if ln < 0, continue; end
    sp = get_param(ln, 'SrcPortHandle');
    dp = get_param(ln, 'DstPortHandle');
    if strcmp(get_param(sp, 'Parent'), blk)
        otherP = dp;
    else
        otherP = sp;
    end
    if slot == 1
        endA = {get_param(otherP, 'Parent'), otherP};
    else
        endB = {get_param(otherP, 'Parent'), otherP};
    end
end

delete_block(h);   % also removes its two lines

jn = [name '_revolute'];
jh = add_block('sm_lib/Joints/Revolute Joint', [mdl '/' jn], ...
               'Position', pos, 'MakeName', 'on');
Lport = get_param(jh, 'LConn');
Rport = get_param(jh, 'RConn');

axisSet = false;
axisNames = {'Axis', 'JointAxis'};
for a = 1:numel(axisNames)
    try
        set_param(jh, axisNames{a}, axis);
        axisSet = true;
        fprintf('  %-28s -> Revolute Joint (axis param "%s" = %s)\n', name, axisNames{a}, axis);
        break;
    catch
    end
end
if ~axisSet
    fprintf('  %-28s -> Revolute Joint. NOTE: could not set the axis parameter programmatically on this release.\n', name);
    fprintf('     Double-click "%s" and set Axis = %s by hand (30 seconds).\n', jn, axis);
end

% rewire: captured end A -> L, end B -> R (handle-based, name-safe)
if ~isempty(endA{1})
    add_line(mdl, endA{2}, Lport, 'autorouting', 'smart');
else
    fprintf('  WARNING: side 1 of "%s" was unconnected - wire %s/L by hand.\n', name, jn);
end
if ~isempty(endB{1})
    add_line(mdl, endB{2}, Rport, 'autorouting', 'smart');
else
    fprintf('  WARNING: side 2 of "%s" was unconnected - wire %s/R by hand.\n', name, jn);
end
fprintf('     weld opened, hinge installed: %s\n', jn);
end
