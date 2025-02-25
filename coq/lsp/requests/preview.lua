(function(...)
  local cancel, cur_session = nil, nil

  COQlsp_preview = function(name, session_id, item)
    cur_session = session_id

    if cancel then
      pcall(cancel)
    end

    local n_clients = 0
    for _ in pairs(vim.lsp.buf_get_clients(0)) do
      n_clients = n_clients + 1
    end

    if n_clients == 0 then
      COQlsp_notify(name, session_id, true, vim.NIL)
    else
      local on_resp_old = function(err, _, resp, client_id)
        if session_id == cur_session then
          n_clients = n_clients - 1
          COQlsp_notify(name, session_id, n_clients == 0, resp or vim.NIL)
        end
      end

      local on_resp_new = function(err, resp, ctx)
        on_resp_old(err, nil, resp, ctx.client_id)
      end

      local on_resp = function(...)
        if type(({...})[4]) == "table" then
          on_resp_new(...)
        else
          on_resp_old(...)
        end
      end

      local ids = {}
      ids, cancel =
        vim.lsp.buf_request(0, "completionItem/resolve", item, on_resp)
    end
  end
end)(...)
