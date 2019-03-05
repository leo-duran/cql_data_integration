# External
from typing import Any

# Internal
from cdi import (Migrate, JavaFunc, Gen, String, Integer, Boolean,NewFK,
                      Path,Overlap,PathEQ,EQ, Conn, NewAttr, NewEntity,CQLExpr,
                      Attr, FK, String,JLit as Lit,Boolean)

from cdi.library_example.models import (
    src,tar,isrc,itar,Chap,Nov,Readr,Chapter,Novel,Reader,Borrow,Author,Library)
################################################################################

####################
# Helper functions #
####################

def concat(*args : Any) -> CQLExpr:
    '''Concatenate a list'''
    if len(args) < 1:
        return args # type: ignore
    out = cat(args[-2],args[-1])
    for a in reversed(args[:-2]):
        out = cat(a,out)
    return out

wild = Lit(".*",String)
##################
# Java Functions #
##################
count_words = JavaFunc('count_words', [String],          Integer, "return 1 + input[0].length() - input[0].replaceAll(' ', '').length()")
Len         = JavaFunc('len',         [String],          Integer, "return input[0].length()")
plus        = JavaFunc('plus', 	      [Integer,Integer], Integer, "return input[0] + input[1]")
matches     = JavaFunc('matches',     [String,String],   Boolean, "return input[0].matches(input[1])")
cat         = JavaFunc('cat',         [String,String],   String,  "return input[0] + input[1]")

funcs = [count_words,Len,plus,matches,cat]

########################################################################
# Map any relevant objs/attrs/relations in source onto paths in target #
########################################################################
chap, nov, readr = Gen('Chap',Chap),Gen('Nov',Nov),Gen('Readr',Readr)

overlap = Overlap(
    s1 = src,
    s2 = tar,

    paths = [
        PathEQ(Path(Nov['title']),
               Path(Novel['title'])),

        PathEQ(Path(Nov['aname']),
               Path(Novel['wrote'],Author['authorname'])),

        PathEQ(Path(Chap['num']),
               Path(Chapter['num'])),

        PathEQ(Path(Chap['novel_id']),
               Path(Chapter['novel'])),

        PathEQ(Path(Readr['rname']),
               Path(Reader['readername'])),

        PathEQ(Path(Readr['fav']),
               Path(Reader['favorite']))
            ],

    new_attr1 = [NewAttr(Chap, 'n_words', Integer, count_words(chap['text'])),],
    new_fk1   = [NewFK(Nov, FK('wrote','Author'),nov)],


    new_ent1  = [
        NewEntity(name = 'Author', gens = [nov]),

        NewEntity(
            name  = 'Borrow',
            gens  = [nov,readr],
            where = [EQ(matches(readr['borrowed'],
                         concat(wild,nov['title'],wild)),
                     Lit('true',Boolean))],
            attrs = {Attr('total_len',Integer): plus(Len(readr['rname']),
                                                     Len(nov['title']))},
            fks   = {FK('r','Readr') : readr,
                     FK('n','Nov')  : nov})],
)

if __name__ == '__main__':
    m  = Migrate(src = src, tar = tar, overlap = overlap, funcs = funcs)
    fi = m.file(src = isrc, tar = itar, merged = Conn(db = 'lib_merged'))
    with open('cdi/library_example/lib.cql','w') as f: f.write(fi)
