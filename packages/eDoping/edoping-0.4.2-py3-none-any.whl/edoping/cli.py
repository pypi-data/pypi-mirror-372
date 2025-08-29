#!/usr/bin/env python3
#
#   Copyright 2023-2025, Jianbo Zhu, Jingyu Li, Peng-Fei Liu
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.


import argparse
import re

from .misc import filein, filecmpot, filetrans, filedata, \
                  __prog__, __description__, __version__, __ref__


def cmd(arg=None):
    footnote = f'>>>>>>>>>> Citation of {__prog__} <<<<<<<<<<\n'\
               f'If you have used {__prog__}, '\
               f'please cite the following article:{__ref__}'
    parser = argparse.ArgumentParser(prog='edp',
                                     description='{} - v{}'.format(__description__, __version__),
                                     formatter_class=argparse.RawDescriptionHelpFormatter, 
                                     epilog=footnote)
    parser.add_argument('-v', '--verbosity', action='count', default=0, help='increase output verbosity')
    parser.add_argument('-q', '--quiet', action='store_true', help='only show key output')
    sub_parser = parser.add_subparsers(title='Tips', metavar='Subcommand', help='Description', dest='task')

    parser_cal = sub_parser.add_parser('cal', help='Calculate defect fromation energy')
    parser_cal.add_argument('-i', '--input', metavar='FILENAME', default=filein, help=f'Assign filename (default: {filein})')

    parser_energy = sub_parser.add_parser('energy', help='Read final energy from OUTCAR')
    parser_energy.add_argument('-f', '--filename', default='OUTCAR', help='Assign filename(default: OUTCAR)')
    parser_energy.add_argument('--ave', '--average', action='store_true', help='Calculate energy per atom')

    parser_ewald = sub_parser.add_parser('ewald', help='Read Ewald from OUTCAR')
    parser_ewald.add_argument('-f', '--filename', default='OUTCAR', help='Assign filename(default: OUTCAR)')
    
    parser_volume = sub_parser.add_parser('volume', help='Read volume from OUTCAR')
    parser_volume.add_argument('-f', '--filename', default='OUTCAR', help='Assign filename(default: OUTCAR)')

    parser_epsilon = sub_parser.add_parser('epsilon', help='Read epsilon from OUTCAR')
    parser_epsilon.add_argument('-f', '--filename', default='OUTCAR', help='Assign filename(default: OUTCAR)')

    parser_evbm = sub_parser.add_parser('evbm', help='Read VBM from EIGENVAL')
    parser_evbm.add_argument('-f', '--filename', default='EIGENVAL', help='Assign filename(default: EIGENVAL)')
    parser_evbm.add_argument('-r', '--ratio', type=float, help='Threshold of filling ratio')
    parser_evbm.add_argument('--ne', type=int, help='The number of electrons(default from the file)')
    parser_evbm.add_argument('--amend', type=int, default=0, help='Additional amendment on nelect')

    parser_fixchg = sub_parser.add_parser('fixchg', help='Produce charge-fixed inputs')
    parser_fixchg.add_argument('-i', '--inputdir', default='charge_0', help='Path to uncharged (q=0) reference files (default: charge_0)')
    parser_fixchg.add_argument('--prefix', default='charge_', help='Prefix of charge-fixed output files (default: charge_)')
    parser_fixchg.add_argument('charges', metavar='CHARGE', type=int, nargs='+', help='The target charge(s)')

    parser_boxhyd = sub_parser.add_parser('boxhyd', help='Place a single hydrogen atom in the box')
    parser_boxhyd.add_argument('-i', '--input', metavar='FILENAME', default='POSCAR', help='Reference structure(default: POSCAR)')
    parser_boxhyd.add_argument('-o', '--output', metavar='FILENAME', default='POSCAR.H', help='Output filename(default: POSCAR.H)')

    parser_refine = sub_parser.add_parser('refine', help='Refine the unit cell')
    parser_refine.add_argument('-t', '--transform', nargs='?', const='TRANSMAT.in', metavar='TRANSMAT', help='Apply the transformation matrix (default: read from TRANSMAT.in)')
    parser_refine.add_argument('-c', '--cubicize', type=int, metavar='NUM', help='Find an almost cubic supercell near the given atom count')
    parser_refine.add_argument('-d', '--displace', nargs=4, metavar=('Site', 'dx', 'dy', 'dz'), help='Make a cartesian displacement in Angstroms (e.g.: Sb3 0 0 0.1)')
    parser_refine.add_argument('-i', '--input', metavar='FILENAME', default='POSCAR', help='Input filename(default: POSCAR)')
    parser_refine.add_argument('-o', '--output', metavar='FILENAME', default='POSCAR', help='Output filename(default: POSCAR)')

    parser_replace = sub_parser.add_parser('replace', help='Replace atoms X by Y')
    parser_replace.add_argument('old', metavar='X', help='Name of previous atom')
    parser_replace.add_argument('new', metavar='Y', help='Name of present atom')
    parser_replace.add_argument('-p', '--position', type=float, nargs=3, metavar=('fa', 'fb', 'fc'), help='Fractional coordinates of new interstitial atom')
    parser_replace.add_argument('-i', '--input', metavar='FILENAME', default='POSCAR', help='Input filename(default: POSCAR)')
    parser_replace.add_argument('-o', '--output', metavar='FILENAME', default='POSCAR', help='Output filename(default: POSCAR)')
    
    parser_groupby = sub_parser.add_parser('groupby', help='Group atoms by radial distribution function')
    parser_groupby.add_argument('-f', '--filename', default='POSCAR', help='Assign filename(default: POSCAR)')
    parser_groupby.add_argument('atom', metavar='ATOM', help='The symbol of element to groupby')
    parser_groupby.add_argument('-p', '--prec', type=float, default=1, help='Precision level for sampling distances(default: 1)')
    parser_groupby.add_argument('--head', type=int, default=30, help='The number of atoms in the nearest neighbor(default: 30)')
    parser_groupby.add_argument('--pad', type=int, default=2, help='Number of values padded to the cell sides(default: 2)')
    parser_groupby.add_argument('--grep', metavar='STRING', help='Display only lines containing the specified atom')
    
    parser_diff = sub_parser.add_parser('diff', help='Show difference between two POSCAR')
    parser_diff.add_argument('-p', '--prec', type=float, default=0.2, help='The precision of distance(default: 0.2)')
    parser_diff.add_argument('-d', '--distance', action='store_true', help='Calculate sum of distances between sites and detected defects')
    parser_diff.add_argument('filename1', help='Filename of the first POSCAR')
    parser_diff.add_argument('filename2', help='Filename of the second POSCAR')
    
    parser_query = sub_parser.add_parser('query', help='Fetch data from OQMD website')
    parser_query.add_argument('--backend', default='OQMD', choices=['OQMD', 'MP'], help='The backend database to query (default: OQMD)')
    parser_query.add_argument('-s', '--structure', action='store_true', help='Fetch structure files at same time')
    parser_query.add_argument('-x', '--extra', default='', help='Extra elements beyond host compound')
    parser_query.add_argument('-t', '--timeout', type=float, default=60, help='The period (in seconds) to await a server reply (default: 60)')
    parser_query.add_argument('-e', '--ehull', type=float, help='Maximum energy hull filter. If not specified, filtering is disabled')
    parser_query.add_argument('-b', '--batch', type=int, default=200, help='The number of entries to retrieve in each request (default: 200)')
    parser_query.add_argument('-o', '--output', metavar='FILENAME', default=filecmpot, help=f'Output filename(default: {filecmpot})')
    parser_query.add_argument('compound', help='The target compound, e.g. Mg2Si')

    parser_chempot = sub_parser.add_parser('chempot', help='Calculate chemical potential')
    parser_chempot.add_argument('-n', '--norm', action='store_true', help='Enable coefficients normalization (if energy/atom is given)')
    parser_chempot.add_argument('-f', '--filename', default=filecmpot, help='Assign filename(default: {})'.format(filecmpot))
    parser_chempot.add_argument('--cond', metavar='WEIGHT', type=float, nargs='+', help='Customized chemical potential conditions')
    parser_chempot.add_argument('--refs', metavar='VALUE', type=float, nargs='+', help='Reference chemical potentials in eV/atom')

    parser_trlevel = sub_parser.add_parser('trlevel', help='Calculate transition levels')
    parser_trlevel.add_argument('-f', '--filename', default=filetrans, help='Assign filename(default: {})'.format(filetrans))
    parser_trlevel.add_argument('--emin', type=float, default=-1, help='The upper bound of Fermi level(default: -1)')
    parser_trlevel.add_argument('--emax', type=float, default= 2, help='The lower bound of Fermi level(default: 2)')
    parser_trlevel.add_argument('-n', '--npoints', type=int, default=1001, help='The number of points(default: 1001)')
    parser_trlevel.add_argument('--fenergy', action='store_true', help='To calculate formation energy')
    parser_trlevel.add_argument('-o', '--output', metavar='FILENAME', default=filedata, help='Output filename(default: {})'.format(filedata))

    parser_scfermi = sub_parser.add_parser('scfermi', help='Calculate sc-fermi level')
    parser_scfermi.add_argument('-t', '--temperature', type=float, default=1000, help='Temperature')
    parser_scfermi.add_argument('filename', metavar='FILENAME', nargs='+', help='Defect formation energy file (*.trans or *.log)')
    parser_scfermi.add_argument('-d', '--dos', metavar='DOSDATA', default='DOSCAR', help='DOSCAR(default) or tdos.dat')
    parser_scfermi.add_argument('--vbm', type=float, default=0, help='Energy of VBM (quite necessary, default:0)')

    # (t, conc, charge, volume, doscar='DOSCAR'):
    parser_fzfermi = sub_parser.add_parser('fzfermi', help='Calculate fz-fermi level')
    parser_fzfermi.add_argument('-t', '--temperature', type=float, default=1000, help='Temperature')
    parser_fzfermi.add_argument('-d', '--dos', metavar='DOSDATA', default='DOSCAR', help='DOSCAR(default) or tdos.dat')
    parser_fzfermi.add_argument('--vbm', type=float, default=0, help='Energy of VBM (quite necessary, default:0)')
    parser_fzfermi.add_argument('conc', type=float, help='Conc of carrier in cm^-3')
    parser_fzfermi.add_argument('charge', type=float, help='Charge of defect')
    parser_fzfermi.add_argument('volume', type=float, help='Volume of cell in A^3')

    # TODO: # (t, *filenames, efermi=(0, ), detail=False)
    # parser_equi = sub_parser.add_parser('equi', help='Confirm the equivalent defect')
    # parser_equi.add_argument('-t', '--temperature', type=float, default=1000, help='Temperature')
    # parser_equi.add_argument('filename', metavar='FILENAME', nargs='+', help='Defect formation energy file')
    # parser_equi.add_argument('--fermi', type=float, nargs='+', default=[0,], help='Fermi level')
    # parser_equi.add_argument('--emin', type=float, default=0, help='The upper bound of Fermi level(default: 0)')
    # parser_equi.add_argument('--emax', type=float, default=1, help='The lower bound of Fermi level(default: 1)')
    # parser_equi.add_argument('-n', '--npoints', type=int, default=0, help='The number of points')
    # parser_equi.add_argument('-r', '--ratio', action='store_true', help='only show key output')
    
    args = parser.parse_args(arg)

    if args.verbosity > 4:
        # debug mode
        raise NotImplementedError
    
    is_quiet = args.quiet
    is_detail = bool(args.verbosity)

    if args.task is None:
        parser.print_help()
    elif args.task == 'cal':
        from .defect import formation
        formation(inputlist=args.input)
    elif args.task == 'energy':
        from .dft import read_energy
        value = read_energy(outcar=args.filename, average=args.ave)
        unit = 'eV/atom' if args.ave else 'eV/cell'
        if is_quiet:
            print('{:.4f}'.format(value))
        else:
            print('Final energy: {:.4f} {}'.format(value, unit))
    elif args.task == 'ewald':
        from .dft import read_ewald
        value = read_ewald(outcar=args.filename)
        if is_quiet:
            print('{:.4f}'.format(value))
        else:
            print('Final (absolute) Ewald: {:.4f}'.format(value))
    elif args.task == 'volume':
        from .dft import read_volume
        value = read_volume(outcar=args.filename)
        if is_quiet:
            print('{:.4f}'.format(value))
        else:
            print('Final volume of cell: {:.4f}'.format(value))
    elif args.task == 'epsilon':
        from .dft import read_epsilon
        # read_epsilon(outcar='OUTCAR', isNumeric=False)
        pf = '{:12.4f}'
        if is_quiet:
            out = read_epsilon(outcar=args.filename, isNumeric=True)
            for _, values in out:
                for value in values:
                    for ivalue in value:
                        print(pf.format(ivalue), end='')
                    print()
        else:
            out = read_epsilon(outcar=args.filename)
            for title, values in out:
                print(title)
                for value in values:
                    print(value)
    elif args.task == 'evbm':
        from .dft import read_evbm, read_evbm_from_ne
        if args.ratio is not None:
            vb, cb, gp = read_evbm(eigenval=args.filename, pvalue=args.ratio)
        else:
            vb, cb, gp = read_evbm_from_ne(eigenval=args.filename,
                                           Ne=args.ne,
                                           dNe=args.amend)
        pf = '{:.4f}'
        pfd = '{:<8.4f} (band #{:<3d}) [{:>9.4f}{:>9.4f}{:>9.4f} ]'
        if is_quiet:
            print(pf.format(cb[0]))  # CBM
        elif is_detail:
            print(('VBM: ' + pfd).format(*vb[:2], *vb[2]))
            print(('CBM: ' + pfd).format(*cb[:2], *cb[2]))
            print(('GAP: ' + pf).format(gp))
        else:
            print(('VBM: ' + pf).format(vb[0]))
            print(('CBM: ' + pf).format(cb[0]))
            print(('GAP: ' + pf).format(gp))
    elif args.task == 'fixchg':
        from .dft import Cell, read_zval, fix_charge
        # Read ZVAL from POTCAR && Check consistency with POSCAR
        if is_detail:
            print('Parsing number of valence electrons from POTCAR and POSCAR in {}...'.format(args.inputdir))
        z_dict = read_zval(potcar='{}/POTCAR'.format(args.inputdir))
        pos = Cell.from_poscar(poscar='{}/POSCAR'.format(args.inputdir))
        epos = ' '.join(pos.sites.keys())
        epot = ' '.join(z_dict.keys())
        if epos != epot:
            raise ValueError('Elements in {0}/POSCAR and {0}/POTCAR are not consistent:\n'
                                '    [{}] vs. [{}]'.format(args.inputdir, epos, epot))

        # Calculate total valence electrons
        total = 0
        for atom, site in pos.sites.items():
            if atom not in z_dict:
                raise ValueError('Cannot find infomation of {} in {}/POTCAR'.format(atom, args.inputdir))
            zi = z_dict[atom]
            num = len(site)
            total += num * zi
            if is_detail:
                print('{:>4s}: {:3g}   ( {} )'.format(atom, zi, num))
        if is_quiet:
            print('{:g}'.format(total))
        else:
            print('Total valence electrons: {:g}'.format(total))

        # Reset NELECT for each provided charge number
        import shutil

        for q in args.charges:
            outdir = '{}{:+g}'.format(args.prefix, q)
            shutil.copytree(args.inputdir, outdir)
            fix_charge('{}/INCAR'.format(outdir), charge=q, nelect=total)
            if not is_quiet:
                print('Produce directory {} successfully.'.format(outdir))
    elif args.task == 'boxhyd':
        from .dft import Cell
        pos = Cell.from_poscar(poscar=args.input)
        poshyd = Cell(basis=pos.basis, sites=[('H', [[0,0,0]]),])
        poshyd.write(args.output)
        if not is_quiet:
            dsp="Save the new structure to '{}' file"
            print(dsp.format(args.output))
    elif args.task =='refine':
        import numpy as np
        from .dft import Cell, read_transmat
        from .defect import supercell, cubicize
        num_opts = sum([
            1 if args.transform else 0,
            1 if args.cubicize else 0,
            1 if args.displace else 0,
        ])
        if num_opts == 0:
            raise ValueError('No refinement option is specified')
        if num_opts > 1:
            raise ValueError('Do not specify multiple refinement options: {}'.format(num_opts))

        if args.transform:
            # for quick test
            trans_mat = read_transmat(args.transform)
            if not is_quiet:
                if args.transform == 'TRANSMAT.in':
                    print('Read transformation matrix from TRANSMAT.in file.')
                else:
                    print("Save transformation matrix to 'TRANSMAT' file")
                if is_detail:
                    print('Transformation matrix:')
                    print(trans_mat)
            pos = Cell.from_poscar(poscar=args.input)
            pos2 = supercell(pos, trans_mat)
            if is_quiet:
                print('{:d}'.format(pos2.get_natom()))
            else:
                print('Build supercell with {} atoms'.format(pos2.get_natom()))
        elif args.cubicize:
            pos = Cell.from_poscar(poscar=args.input)
            nref = args.cubicize
            trans_mat, nreal = cubicize(pos, nref)
            trans_mat = read_transmat(trans_mat)    # check format and save to TRANSMAT
            if is_quiet:
                print('{:d}'.format(nreal))
            else:
                print('Found a (almost) cubic cell with {} atoms.'.format(nreal))
                print("Save transformation matrix to 'TRANSMAT' file.")
                if is_detail:
                    print('Transformation matrix:')
                    print(trans_mat)
            pos2 = supercell(pos, trans_mat)
        elif args.displace:
            pos = Cell.from_poscar(poscar=args.input)
            site_, dx_, dy_, dz_ = args.displace
            site = re.match(r'([a-zA-Z]+)(\d*)', site_)
            if site:
                atom, idx = site.groups()
                idx = int(idx) if idx else 1
                if atom not in pos.sites:
                    raise ValueError('Cannot find atom: {}'.format(atom))
                if (idx < 1) or (idx > len(pos.sites[atom])):
                    raise ValueError('Invalid index: {}'.format(idx))
                dr_cart = np.array([float(v) for v in [dx_, dy_, dz_]])
                distance = np.linalg.norm(dr_cart)
                if is_detail:
                    print('Displace {}{} by ({:.4f}, {:.4f}, {:.4f}), {:.4g} Angstroms'.format(atom, idx, *dr_cart, distance))
                elif is_quiet:
                    print('{:.4g}'.format(distance))
                else:
                    print('Displace {}{} by {:.4g} Angstroms'.format(atom, idx, distance))
                dr_frac = dr_cart @ np.linalg.inv(pos.basis)
                pos.sites[atom][idx-1] += dr_frac - np.floor(dr_frac)
            else:
                raise ValueError('Invalid site format: {}'.format(site_))
            pos2 = pos
        pos2.write(poscar=args.output)
        if not is_quiet:
            print(f"Save the new POSCAR to '{args.output}' file")
    elif args.task == 'replace':
        from .dft import Cell
        poscar = Cell.from_poscar(poscar=args.input)
        old = re.match(r'([a-zA-Z]+)(\d*)', args.old)
        if old:
            atom, idx = old.groups()
            atom_old = {
                'atom': atom,
                'idx': int(idx) if idx else 1
            }
        else:
            raise ValueError('Invaild value: {}'.format(args.old))

        if atom_old['atom'].lower().startswith('vac'):
            if args.position is None:
                raise ValueError('Position of interstitial atom is required by --position option.')
            loc = args.position
        else:
            loc = poscar.pop(**atom_old)

        new = re.match(r'([a-zA-Z]+)', args.new)
        if new:
            atom_new = {
                'atom': new.groups()[0],
                'pos': loc
            }
        else:
            raise ValueError('Invaild value: {}'.format(args.new))

        if not atom_new['atom'].lower().startswith('vac'):
            poscar.insert(**atom_new)

        poscar.write(poscar=args.output)
        dsp = 'Replace {} by {}, and new structure is saved to {}'
        if not is_quiet:
            label_old = '{}{}'.format(atom_old['atom'], atom_old['idx'])
            label_new = '{}'.format(atom_new['atom'])
            print(dsp.format(label_old, label_new, args.output))
    elif args.task == 'groupby':
        from itertools import zip_longest
        from .dft import Cell
        from .defect import cal_rdf
        atom = args.atom
        prec = args.prec
        pos = Cell.from_poscar(poscar=args.filename)
        if atom not in pos.sites:
            raise ValueError('Cannot find atom: {}'.format(atom))

        # calculate RDF for each atom site and group them by the RDF
        rdfs_full = cal_rdf(
            pos,
            centres=[(atom, idx+1) for idx in range(len(pos.sites[atom]))],
            nhead=args.head,
            npad=args.pad,
            prec=pow(10, prec),
        )
        rdf_group = dict()
        for i, rdf in enumerate(rdfs_full):
            rdf_group.setdefault(tuple(rdf), []).append(f'{atom}{i+1}')
        rdfs_unique = list(rdf_group.keys())

        for i, k in enumerate(rdfs_unique):
            print('Group #{}: {}'.format(i+1, ', '.join(rdf_group[k])))
        if not is_quiet:
            ngroup = len(rdfs_unique)
            digits = int(prec + 0.999999) if prec > 0 else 0
            nwidth = 17 + digits if digits > 2 else 19
            fmt1, fmt2 = '(%.{}f'.format(digits), ", '%s', %d)"
            fmt = '%{}s%-{}s'.format(nwidth-12, 12)
            fdst = lambda d, e, n: fmt % (fmt1 % (d/pow(10, prec)), fmt2 % (e, n))
            fmd = '%{}s%-{}d'.format(nwidth//2 + 3, nwidth - nwidth//2 - 3)
            fdsd = lambda i: fmd % ('Group #', i)

            print()
            print('===', *(['='*nwidth,] * ngroup), sep='=')
            print('No.', *[fdsd(i+1) for i in range(ngroup)], sep='|')
            print('---', *(['-'*nwidth,] * ngroup), sep='+')
            for i, dts in enumerate(zip_longest(*rdfs_unique, fillvalue=(0, 'X', 0))):
                line = f'{i:^3d}|' + '|'.join([fdst(*dt) for dt in dts])
                if (not args.grep) or (f"'{args.grep}'" in line): print(line)
            print('===', *(['='*nwidth,] * ngroup), sep='=')
    elif args.task == 'diff':
        from .dft import Cell
        from .defect import diff_cell, disp_diffs
        c1 = Cell.from_poscar(poscar=args.filename1)
        c2 = Cell.from_poscar(poscar=args.filename2)
        diffs = diff_cell(c1, c2, prec=args.prec)
        disp_diffs(c1.basis, diffs,
                   full_list=is_detail,
                   with_dist=args.distance)
    elif args.task == 'query':
        from .query import get_phases
        elmt_comp = re.findall(r'[A-z][a-z]*', args.compound)
        elmt_extra = re.findall(r'[A-z][a-z]*', args.extra)
        elmt_all = list(elmt_comp)
        for elt in elmt_extra:
            if elt not in elmt_all:
                elmt_all.append(elt)
        # elmt_all = sorted(set(elmt_comp + elmt_extra))
        if not is_quiet:
            print(f'Searching for phases with elements: {elmt_all}')
        phases_all = get_phases(
            elements=elmt_all,
            max_ehull=args.ehull,
            include_struct=args.structure,
            backend=args.backend,
            timeout=args.timeout,
            batch=args.batch,
        )

        if is_detail:
            print(f'Number of phases fetched from {args.backend} database: {len(phases_all)}')

        # remove duplicate phases according fromation energy (delta_e)
        phases_uni = dict()
        for phase in phases_all:
            name, delta_e = phase['name'], phase['delta_e']
            if (name not in phases_uni) or (delta_e < phases_uni[name]['delta_e']):
                phases_uni[name] = phase
        phases = list(phases_uni.values())

        if not is_quiet:
            print(f'Number of ground-state phases found: {len(phases)}')

        get_comp = lambda name: {m[0]: int(m[1] or '1') 
            for m in re.findall(r'([A-Z][a-z]*)(\d*\.\d+|\d+)?', name)}
        
        cmpots = ['# {}\n'.format('   '.join(elmt_all)), ]    # header line
        dsp = ' {} '*(len(elmt_all)+1) + '\n'
        dsp_head = f'POSCAR generated by {__prog__}: '\
                  '{name} (id: {id}) {delta_e:.6f} {ehull:.6f}'
        dsp_fout = 'POSCAR.{name}.vasp'
        dsp_disp = '    {name:<10} {delta_e:>12.6f}      {id}'
        
        target = get_comp(args.compound)
        ratios = [target.get(e, 0) for e in elmt_all]
        cmpots.append(dsp.format(*ratios, '_Not_found_'))
        target_found = False

        if is_detail:
            print('   name             delta_e      IDs')
        export_struct = args.structure
        for phase in phases:
            comp = get_comp(phase['name'])
            ratios = [comp.get(e, 0) for e in elmt_all]
            delta_e = phase['delta_e']
            line = dsp.format(*ratios, delta_e)
            if comp == target:
                cmpots[1] = line
                target_found = True
            else:
                cmpots.append(line)
            if export_struct:
                pos = phase['struct']  # Cell object
                fname = dsp_fout.format(**phase)
                header = dsp_head.format(**phase)
                pos.write(fname, header=header)
            if is_detail:
                print(dsp_disp.format(**phase))
        with open(args.output, 'w') as f:
            f.writelines(cmpots)
        if not is_quiet:
            end_info = '. (DONE)' if target_found else '\n'
            print(f'Data saved to {args.output}{end_info}')
        if not target_found:
            print(f'WARNING: Target compound "{args.compound}"'
                  ' is not included in the retrieved data.\n')
    elif args.task == 'chempot':
        from .cpot import pminmax
        # pminmax(filename, objcoefs=None)
        # return (name, x0, status, msg),labels
        results,labels = pminmax(args.filename, 
                                 objcoefs=args.cond,
                                 referance=args.refs,
                                 normalize=args.norm)
        if is_quiet:
            for rst in results:
                if is_detail:
                    print('{:^5d}'.format(rst[2]), end='')
                if rst[1] is None:
                    raise RuntimeError(f'No solution found\n  {rst[3]}')
                for miu in rst[1]:
                    print('{:<10.4f}'.format(miu), end='')
                print()
        else:
            dsp1 = '{:^8d}{:<10s}'
            dsp2 = '{:>10.4f}'
            dsp3 = '   {:<s}'
            
            header = '{:8s}{:10s}'.format('status', 'condition')
            for elmt in labels:
                header += '{:>10s}'.format('miu('+elmt+')')
            if is_detail:
                header += '   {:<s}'.format('Information')  
            print(header)
            
            for rst in results:
                print(dsp1.format(rst[2], rst[0]), end='')
                if rst[1] is None:
                    raise RuntimeError(f'No solution found\n  {rst[3]}')
                for miu in rst[1]:
                    print(dsp2.format(miu), end='')
                if is_detail:
                    print(dsp3.format(rst[3]))
                else:
                    print()
    elif args.task == 'trlevel':
        from .defect import read_H0, cal_trans, write_bsenergy
        data, volume = read_H0(args.filename)
        q, H0 = data[:,0].astype('int32'), data[:,1]
        result, bsdata = cal_trans(q, H0, args.emin, args.emax, 
                                   Npt=args.npoints, outbsline=True)
        if not is_quiet:
            header = ('Valence', 'E_trans/eV', 'E_defect/eV')
            print('  {:^12s}  {:^12s}  {:^12s}'.format(*header))  
        dsp = '  {:^12s}  {:^12.2f}  {:^12.2f}'
        for line in result:
            print(dsp.format(*line))
        print()
        
        if args.fenergy:
            write_bsenergy(bsdata, q, args.output, volume, 1)
            if not is_quiet and is_detail:
                print('Save formation eneryg data to {}.'.format(args.output))
        
    elif args.task == 'scfermi':
        from .fermi import scfermi
        # scfermi(t, *filenames, doscar='DOSCAR', Evbm=0, detail=False)
        out = scfermi(args.temperature, 
                      *args.filename, 
                      doscar=args.dos, 
                      Evbm=args.vbm,
                      detail=is_detail)
        dsp = ('Self-consistent Fermi level (eV)',
               'Equilibrium carrier concentration (cm^-3)',
               'Net number of electron in cell')
        if is_quiet:
            # not_detail: EF, Ne
            #  is_detail: n_p, EF, Ne 
            print(*out)
        elif is_detail:
            n_p, EF, Ne = out
            print('{} : {:.3f}'.format(dsp[0], EF))
            print('{} : {:.4E}'.format(dsp[1], Ne))
            print('{} : {:+.6E}'.format(dsp[2], n_p))
        else:
            EF, Ne = out
            print('{} : {:.3f}'.format(dsp[0], EF))
            print('{} : {:.4E}'.format(dsp[1], Ne))
    elif args.task == 'fzfermi':
        from .fermi import scfermi_fz
        # scfermi_fz(t, conc, charge, volume, doscar='DOSCAR', Evbm=0)
        out = scfermi_fz(t=args.temperature, 
                         conc=args.conc, 
                         charge=args.charge, 
                         volume=args.volume, 
                         doscar=args.dos,
                         Evbm=args.vbm,
                         detail=is_detail)
        dsp = ('Formation energy: H(Ef) = {:.2f} {:+.3f}*Ef',
               'Formation energy at sc-Ef({:.2f} eV): {:.2f} eV/u.c.',
               'Net number of electron in cell: {:+.6E}')
        if is_quiet:
            # not_detail: DH0, DHq, Ef
            #  is_detail: n_p, DH0, DHq, Ef
            print(*out)      
        elif is_detail:
            n_p, DH0, DHq, Ef = out
            print(dsp[0].format(DH0, args.charge))
            print(dsp[1].format(Ef, DHq))
            print(dsp[2].format(n_p))
        else:
            DH0, DHq, Ef = out
            print(dsp[0].format(DH0, args.charge))
            print(dsp[1].format(Ef, DHq))
    elif args.task == 'equi':
        from .fermi import equ_defect
        # equ_defect(t, *filenames, efermi=(0, ), detail=False)
        # not_detail: header, (Ef, q_eff, H_eff)
        #  is_detail: header, (Ef, q_eff, H_eff, Ntot, Nq)
        if args.npoints == 0:
            fermi = args.fermi
        else:
            E0, E1, N = args.emin, args.emax, args.npoints
            dE = (E1-E0)/N
            fermi = [E0+i*dE for i in range(N+1)]
        out = equ_defect(args.temperature,
                         *args.filename,
                         efermi=fermi,
                         detail=is_detail)
        
        def disp(data, header=None):
            if header is not None:
                print(header)
            for dd in data:
                Ef, q_eff, H_eff, *Nq = dd
                print('{:10.4f}{:10.4f}{:10.4f}'.format(Ef, q_eff, H_eff),end='')
                for ni in Nq:
                    print('{:10.3E}'.format(ni), end='')
                print()
        
        header, data = out
        if is_detail and args.ratio:
            data[:,4:] /= data[:,3:4]
            
        if is_quiet:
            disp(data)
        else:
            disp(data, header)


if __name__ == '__main__':
    cmd()
