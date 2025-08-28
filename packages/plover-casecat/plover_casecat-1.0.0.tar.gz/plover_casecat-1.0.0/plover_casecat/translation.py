def ploverify_translation(tl):
  final_tl = ""

  idx = 0
  while idx < len(tl):
    ch = tl[idx]

    if ch == 0x01:
      # non-breaking space, aka "sticky space"
      # equivalent to \~ in RTF
      final_tl += "\xa0"
      idx += 1
    elif ch == 0x02:
      # each conflict is preceded by \x02, then the last one is followed by \x03
      # \x02 their \x02 there \x02 they're \x03
      conflict_end = tl.find(0x03, idx + 1)
      if not conflict_end:
        # unterminated conflict
        raise ValueError

      options = tl[idx + 1 : conflict_end].split(b"\x02")
      final_tl = f"[{'|'.join(opt.decode('utf-8') for opt in options)}]"

      idx = conflict_end + 1
    elif ch == 0x04:
      final_tl += "{^}"
      idx += 1
    elif ch == 0x09:
      final_tl += "{^\t^}"
      idx += 1
    elif ch == 0x0A:
      final_tl += "{^\n^}"
      idx += 1

    elif ch == 0x10:
      sub_command = tl[idx + 1]

      if sub_command == 0x81 or sub_command == 0x02:
        # 10 81 = prefix, 10 02 = glue
        glue = sub_command == 0x02

        end_of_word = tl.find(0x20, idx + 2)
        if end_of_word == -1:
          inner_tl = ploverify_translation(tl[idx + 2 :])
          if glue:
            final_tl += f"{{&{inner_tl}}}"
          else:
            final_tl += f"{{^{inner_tl}}}"
          idx = len(tl)
          break
        else:
          inner_tl = ploverify_translation(tl[idx + 2 : end_of_word])
          if glue:
            final_tl += f"{{&{inner_tl}}} "
          else:
            final_tl += f"{{^{inner_tl}}} "
          idx = end_of_word + 1
      elif sub_command == 0x01:  # 10 01 = prefix
        if " " in final_tl:
          rest, last_word = final_tl.rsplit(" ", 1)
          final_tl = f"{rest} {{{last_word}^}}"
        else:
          final_tl = f"{{{final_tl}^}}"
        idx += 2
      elif sub_command == 0x03:  # 10 03 = define/add translation
        return "{plover:add_translation}"
      elif sub_command == 0x0C:  # 10 0c = delete stroke
        return "=undo"
      elif sub_command == 0x41:  # 10 41 = cap previous 1 word
        final_tl += "{*-|}"
        idx += 2
      else:
        raise ValueError

    elif ch == 0x12:
      sub_command = tl[idx + 1]

      if sub_command == 0x08:  # 12 08 = all caps on
        return "{mode:caps}"
      elif sub_command == 0x88:  # 12 88 = all caps off
        return "{mode:reset_case}"
      elif sub_command == 0x0E:  # 12 0e = cap next
        return "{-|}"
      elif sub_command == 0x8E or sub_command == 0x0C:
        # 12 8e = uncap next, 12 0c = force next lowercase
        return "{>}"
      else:
        idx += 2

    elif ch == 0x15:
      raise ValueError

    elif ch == 0x16:
      # 16 xx 00 = paragraph style xx
      paragraph_type = tl[idx + 1]

      if paragraph_type == 0x02:  # question
        final_tl += "{^}\nQ.{-|}"
      elif paragraph_type == 0x03:  # answer
        final_tl += "{^}\nA.{-|}"
      else:
        final_tl += "{^\n^}"

      idx += 3

    elif ch >= 0x20:
      final_tl += chr(ch)
      idx += 1

    else:
      raise ValueError

  return final_tl
