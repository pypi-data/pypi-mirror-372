import {EditorView} from "@codemirror/view";
import {EditorState} from "@codemirror/state";
import {modifyFirstLineFormat} from "../../ConnectionMagicFormat/FormatConnectMagic";


describe('test applyReadonly', () => {
  it('test applyReadonly should mark first line in cell readonly if start with %%connect', function () {
    const parent = document.createElement('div')
    const state = EditorState.create({
      doc: '%%connect \n abc'
    });
    const e = new EditorView({parent, state})
    const result = modifyFirstLineFormat(e)
    expect(result.size).toBe(1)
    expect(result.iter(0).value?.spec?.class).toBe("cm-hide-connect-magic")
  });
  it('test applyReadonly should not mark first line in cell readonly if start with %%connect', function () {
    const parent = document.createElement('div')
    const state = EditorState.create({
      doc: 'test'
    });
    const e = new EditorView({parent, state})
    const result = modifyFirstLineFormat(e)
    expect(result.size).toBe(0)
  });
});
