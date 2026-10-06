using Ambermoon;
using Ambermoon.Data;
using Ambermoon.Data.Enumerations;
using Ambermoon.Data.Legacy;
using Attribute = Ambermoon.Data.Attribute;

// Dumps party member, spell and spell scroll data of the original and Ambermoon Advanced as TSV files.
string outDir = args[0];
var datasets = new (string Name, string Path, Features Features)[]
{
    ("original", args[1], Features.None),
    ("advanced", args[2], Features.AmbermoonAdvanced | Features.AdvancedMonsterFlags | Features.ItemElements | Features.ExtendedLanguages | Features.LevelShards),
};

foreach (var (name, path, features) in datasets)
{
    var gameData = new GameData(GameData.LoadPreference.ForceExtracted, null, false);
    gameData.Load(path);

    using (var writer = new StreamWriter(Path.Combine(outDir, $"party_{name}.tsv")))
    {
        writer.WriteLine("index\tname\tclass\tmastery\tlevel\tslp\tslp_per_level\tsp_max\tsp_per_level\tint\tint_max\tint_bonus\tread_magic\tread_magic_max\tuse_magic\tlearned");
        foreach (var (pm, i) in gameData.CharacterManager.InitialPartyMembers.Select((p, i) => (p, i + 1)))
        {
            if (pm == null)
                continue;
            var intel = pm.Attributes[Attribute.Intelligence];
            var rm = pm.Skills[Skill.ReadMagic];
            var um = pm.Skills[Skill.UseMagic];
            writer.WriteLine($"{i}\t{pm.Name}\t{pm.Class}\t{(int)pm.SpellMastery:X2}\t{pm.Level}\t{pm.SpellLearningPoints}\t{pm.SpellLearningPointsPerLevel}\t" +
                $"{pm.SpellPoints.MaxValue}\t{pm.SpellPointsPerLevel}\t{intel.CurrentValue}\t{intel.MaxValue}\t{intel.BonusValue}\t{rm.CurrentValue}\t{rm.MaxValue}\t{um.CurrentValue}\t" +
                string.Join(",", pm.LearnedSpells.Select(s => (int)s)));
        }
    }

    using (var writer = new StreamWriter(Path.Combine(outDir, $"spells_{name}.tsv")))
    {
        writer.WriteLine("spell\tenum\tschool\tsp\tslp");
        foreach (var (spell, info) in SpellInfos.Entries.OrderBy(e => e.Key))
        {
            if ((int)spell > 120)
                continue;
            writer.WriteLine($"{(int)spell}\t{spell}\t{info.SpellSchool}\t{SpellInfos.Entries.GetSPCost(features, spell, null!)}\t{SpellInfos.Entries.GetSLPCost(features, spell)}");
        }
    }

    using (var writer = new StreamWriter(Path.Combine(outDir, $"scrolls_{name}.tsv")))
    {
        writer.WriteLine("item\tname\tspell\tclasses\tprice");
        foreach (var item in gameData.ItemManager.Items.Where(i => i.Type == ItemType.SpellScroll))
            writer.WriteLine($"{item.Index}\t{item.Name}\t{(int)item.Spell}\t{item.Classes}\t{item.Price}");
    }

    Console.WriteLine($"{name}: done");
}
